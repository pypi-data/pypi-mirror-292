# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import importlib
import json
import ssl
import logging
import typing
import socket
from pathlib import Path
from sys import exit as sys_exit

from atckit.utilfuncs import UtilFuncs
import argstruct

from convection.shared.config import ConvectionConfigCore, ConvectionConfiguration
from convection.shared.functions import get_actions
from convection.shared.exceptions import AuthenticationError

class SecretsClientMethodsCore:
    """Convection Secrets Client
    """
    _SERVICE_NAME:str = "convection-secrets"
    _SERVICE_SHUTDOWN_LIMIT:int = 300

    config:ConvectionConfigCore
    logger:logging.Logger
    _ssl_context:ssl.SSLContext
    _config_file:Path
    _config_path:Path
    _config:dict[str,typing.Any]
    _tls_ca:Path
    _socket_path:Path
    _config_prefix:str
    _server_ip:str
    _server_port:int
    _argstruct:argstruct.ArgStruct
    _action_map:dict[str,typing.Callable[[ssl.SSLSocket,typing.Union[tuple[str,int],str,None],typing.Union[dict[str,typing.Any],None]],None]]
    _connected:bool
    _connection:typing.Union[ssl.SSLSocket,None]

    _auth_token:typing.Union[str,None]
    _access_key_id:typing.Union[str,None]

    ACL_MODE_ALLOW:int = 1
    ACL_MODE_DENY:int = 0
    ACL_MODE_INVALID:int = -1

    ACL_ACCESS_MODE_INVALID:int = 224
    ACL_ACCESS_MODE_NONE:int = 0
    ACL_ACCESS_MODE_READ:int = 2
    ACL_ACCESS_MODE_WRITE:int = 4
    ACL_ACCESS_MODE_MODIFY:int = 8
    ACL_ACCESS_MODE_DELETE:int = 16

    ACL_TYPE_GENERIC:str = "ACLObject"
    ACL_TYPE_COMMAND:str = "ACLCommand"
    ACL_TYPE_STORE:str = "ACLStore"

    ATTACH_ACL_GROUP:str = "group"
    ATTACH_ACL_USER:str = "user"

    @property
    def connected(self) -> bool:
        """Whether Connection has been opened or not
        @retval bool Connected
        """
        return self._connected

    def __init__(self) -> None:
        self._access_key_id = None
        self._auth_token = None
        self._connected = False
        self._connection = None
        self.logger = UtilFuncs.create_object_logger(self)
        try:
            self.config = ConvectionConfiguration.instance
            self._config_prefix = "global.secrets.client"
        except BaseException:
            self.logger.debug("Failed to get ConvectionConfiguration instance, likely server only mode")
            self._config_prefix = "service"
            return
        self._load()
        if self.config.get_configuration_value(f"{self._config_prefix}.use_network"):
            self._server_ip:str = self.config.get_configuration_value(f"{self._config_prefix}.network.target_ip")
            self._server_port:int = int(self.config.get_configuration_value(f"{self._config_prefix}.network.target_port"))

    def have_tls_ca(self) -> bool:
        """CA Cert configred/existence Check
        @retval bool CA Cert configured and is file
        """
        try:
            tls_path:str = self.config.get_configuration_value(f"{self._config_prefix}.tls_ca")
        except ValueError:
            return False
        p:Path = Path(tls_path).resolve()
        return p.is_file()

    def get_configuration_value(self,name:str,prefix:bool = False) -> typing.Any:
        """Config Getter passthrough
        @param str \c name Name of Item to get
        @param bool \c prefix Whether or not to prepend the configured `_config_prefix` to the item name
        @retval Any Configuration Value
        """
        item_name:str
        if not prefix:
            item_name = name
        else:
            item_name = f"{self._config_prefix}.{name}"
        return self.config.get_configuration_value(item_name)

    def load_standalone(self,call_args:dict[str,typing.Any]) -> None:
        """Standalone Configuration Initializer
        Used for Service Specific / CLI operations
        @param dict[str,Any] \c call_args Commandline Arguments
        @retval None Nothing
        """
        if "config_prefix" in call_args.keys():
            self._config_prefix = call_args.pop("config_prefix")
        specker_root:str = "secrets-controller"
        if "specker_root" in call_args.keys():
            specker_root = call_args.pop("specker_root")
        config_root:Path = Path(call_args["config"]).resolve()
        config_path:typing.Union[Path,None]
        if config_root.is_file():
            config_path = config_root
        else:
            UtilFuncs.add_config_search_path(config_root)
            config_path = UtilFuncs.find_config_file(self._SERVICE_NAME,self._SERVICE_NAME)
            UtilFuncs.remove_config_search_path(config_root)
        if config_path is None:
            self.logger.critical(f"Unable to locate configuration file for {self._SERVICE_NAME}")
            self._config = {}
        else:
            self._config_file = config_path
            self._config_path = config_path.parent
            config_file_str:str = self._config_file.as_posix()
            self.logger.debug(f"Loading {config_file_str}")
            self._config = UtilFuncs.load_sfile(self._config_file)
        try:
            self.config = ConvectionConfigCore(specker_root,self._config)
        except BaseException as e:
            self.logger.critical(f"{type(e).__qualname__} - {e}")
            raise type(e)(e) from e
        self._load()
        if self.config.get_configuration_value(f"{self._config_prefix}.use_network"):
            self._server_ip:str = self.config.get_configuration_value(f"{self._config_prefix}.network.listen_ip")
            self._server_port:int = int(self.config.get_configuration_value(f"{self._config_prefix}.network.listen_port"))

    def _load(self) -> None:
        """TLS Initializer
        Init TLS Context, load CA Cert, etc
        @retval None Nothing
        """
        logging_fh:logging.FileHandler = logging.FileHandler(self.config.get_configuration_value(f"{self._config_prefix}.log_file"))
        logging.getLogger().addHandler(logging_fh)
        self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self._ssl_context.minimum_version = ssl.TLSVersion.TLSv1_3
        self._ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
        use_network:bool = self.config.get_configuration_value(f"{self._config_prefix}.use_network")
        if not bool(use_network):
            self._ssl_context.check_hostname = False
            self._socket_path:Path = Path(self.config.get_configuration_value(f"{self._config_prefix}.socket_path")).resolve()
        if self.have_tls_ca():
            tls_path:str = self.config.get_configuration_value(f"{self._config_prefix}.tls_ca")
            self._tls_ca:Path = Path(tls_path).resolve()
            if not self._tls_ca.is_file():
                tls_ca_str:str = self._tls_ca.as_posix()
                self.logger.critical(f"TLS CA was configured, but does not exist at {tls_ca_str}")
                sys_exit(1)
            self._ssl_context.load_verify_locations(self._tls_ca)
        else:
            self.logger.warning("===============================================================")
            self.logger.warning(" NO TLS CA WAS CONFIGURED. THIS IS SUBOPTIMAL")
            self.logger.warning(f" You should configure {self._config_prefix}.tls_ca")
            self.logger.warning("===============================================================")
            self._ssl_context.check_hostname = False
            self._ssl_context.verify_mode = ssl.CERT_NONE

        self._action_map = get_actions(self)
        shared_path:Path = Path(importlib.import_module("convection.shared").__path__[0]).resolve()
        m_path:Path = shared_path.joinpath("convection-sm-commands.toml")
        spec_path:Path = shared_path.joinpath("specs/").resolve()
        self._argstruct = argstruct.ArgStruct(m_path,"toml",[spec_path])

    def command(self,command:str,data:typing.Union[dict[str,typing.Any],None] = None) -> typing.Union[dict[str,typing.Any],None]:
        """General Command Send, Read
        @param str \c command Command Name to Send
        @param Union[dict[str,Any],None] Data for Command
        @retval Union[dict[str,Any],None] None if no data returned, Result Object otherwise
        """
        if command not in self._argstruct.commands.keys():
            raise LookupError(f"'{command}' is not a valid command")
        self.connect()
        if not self.connected or self._connection is None:
            self.logger.error("Unable to connect to server. See previous errors")
            raise ConnectionError("Unable to connect to server. See previous errors")
        command_data:argstruct.ArgStructCommand = self._argstruct.commands[command]
        if command_data.get("auth_required"):
            if data is None:
                data = {}
            data = self._attach_auth_data(data)
        else:
            if self._access_key_id is not None:
                if data is None:
                    data = {}
                data["access_key_id"] = self._access_key_id
        if data is not None:
            data["command"] = command
            data = argstruct.parse(self._argstruct,data,"command")
            data.pop("command") # type: ignore
            if data is None:
                raise ValueError("Argument processing failed")
        self._send_command(command=command,data=data)
        return self._read_result()

    def _attach_auth_data(self,request_data:dict[str,typing.Any]) -> dict[str,typing.Any]:
        """Authentication Data attachment
        @param dict[str,Any] \c request_data Assembled Request Data
        @retval dict[str,Any] Request Data with Authentication data attached
        """
        if self._access_key_id is None or self._auth_token is None:
            self.logger.error("Not Authenticated")
            raise AuthenticationError()
        request_keys:list[str] = list(request_data.keys())
        if "access_key_id" in request_keys and "auth_token" in request_keys:
            self.logger.debug("NOTE: Skipping Auth Data Attachment, Request already provides AccessKeyID and AuthToken")
            return request_data
        request_data["access_key_id"] = self._access_key_id
        request_data["auth_token"] = self._auth_token
        return request_data

    def _send_command(self,command:str,data:typing.Union[dict[str,typing.Any],None] = None) -> None:
        """RAW Send Data to Server
        @param ssl.SSLSocket \c conn Remote Connection
        @param str \c command Command Name to Send
        @param Union[dict[str,Any],None] Data for Command
        @retval None Nothing
        """
        self.logger.debug(f"Sending Command: '{command}'")
        send_data:bytes = bytes(command,"utf-8")
        if data is not None:
            data_str:str = json.dumps(data)
            send_data += bytes(" ","utf-8")
            send_data += bytes(data_str,"utf-8")
        if self._connection is None:
            raise ConnectionError("Not Connected")
        self._connection.sendall(send_data)

    def _read_result(self) -> typing.Union[dict[str,typing.Any],None]:
        """RAW Read Data from Server
        @param ssl.SSLSocket \c conn
        @retval Union[dict[str,Any],None] None if no data returned, Result Object otherwise
        """
        if self._connection is None:
            raise ConnectionError("Not Connected")
        result:bytes = self._connection.read()
        if len(result) > 0:
            out:dict[str,typing.Any] = json.loads(result.decode("utf-8")) # mypy: type=ignore # type: ignore
            return out
        return None

    def connect(self) -> ssl.SSLSocket:
        """Connect to Server
        @retval ssl.SSLSocket Server Connection
        Also sets _connection to same ssl.SSLSocket
        """
        if self.connected and self._connection is not None:
            self.logger.debug("Already Connected")
            return self._connection
        sock_type:int
        conn_target:typing.Union[str,tuple[str,int]]
        hostname:typing.Union[str,None]
        if not bool(self.config.get_configuration_value(f"{self._config_prefix}.use_network")):
            self.logger.info("Connecting via Socket")
            sock_type = socket.AF_UNIX
            conn_target = self._socket_path.as_posix()
            hostname=None
        else:
            self.logger.info("Connecting via Network")
            sock_type = socket.AF_INET
            conn_target = (self._server_ip,self._server_port)
            hostname = self._server_ip
        sock = socket.socket(sock_type, socket.SOCK_STREAM)
        conn:ssl.SSLSocket = self._ssl_context.wrap_socket(sock,server_hostname=hostname)
        self.logger.info(f"Connecting to Server {conn_target}")
        try:
            conn.connect(conn_target)
            conn.do_handshake(True)
            self._connected = True
        except (ConnectionError,FileNotFoundError) as e:
            self.logger.critical(f"Error during Connection: {e}")
            self._connected = False
        self._connection = conn
        return conn

    def close(self) -> None:
        """Close Connection
        @param ssl.SSLSocket \c conn Server Connection
        @retval None Nothing
        """
        if not self.connected or self._connection is None:
            return
        self._connection.send(bytes("close",encoding="utf-8"))
        self._connection.close()
        self._connected = False
        self._connection = None
