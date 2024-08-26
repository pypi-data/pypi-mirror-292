# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import importlib
import json
import logging
import os
import typing
import argparse
from pathlib import Path
from sys import exit as sys_exit

from tabulate import tabulate

import argstruct
from atckit.utilfuncs import UtilFuncs

from convection.shared.functions import get_actions,get_config_types,exit_invalid_cmd, print_console_initialization_data

from convection.secrets.client import ConvectionSecretsClient

class ConvectionSecretsConsole:
    """Convection Secrets Manager Console Actions
    """

    _KEYDB_NOTICE:list[list[str]] = [
        ["WARNING: A new RootKey has been generated!!!"],
        ["LOSS OF THESE KEYS WILL RESULT IN DATA LOSS"],
        [""],
        ["ONE OF THESE KEYS WILL NEED TO BE PASSED TO THE SECRETS MANAGER DURING UNLOCK COMMANDS"],
        ["IT IS RECOMMENDED TO CHOOSE ONE FOR CONSTANT USE, AND STORE THE OTHERS SECURELY AWAY"],
        [""],
        ["AN UNLOCK COMMAND MUST NOW BE SENT TO CONTINUE USE"]
    ]

    logger:logging.Logger
    client:ConvectionSecretsClient
    _config_prefix:str
    _action_map:dict[str,typing.Callable]
    _argstruct:argstruct.ArgStruct

    def __init__(self,input_args:dict[str,typing.Any]) -> None:
        """Initializer
        @param dict[str,Any] input_args CLI/Console Args
        """
        self.logger = UtilFuncs.create_object_logger(self)
        self.client = ConvectionSecretsClient()
        self.client.load_standalone(input_args)
        if not self.client.have_tls_ca():
            print("===============================================================")
            print(" NO TLS CA WAS CONFIGURED. THIS IS SUBOPTIMAL")
            print(" You should configure global.secrets.client.tls_ca")
            print("===============================================================")
        self._action_map = get_actions(self)
        m_path:Path = Path(importlib.import_module("convection.shared").__path__[0]).resolve().joinpath("convection-sm-commands.toml")
        self._argstruct = argstruct.ArgStruct(m_path,"toml")

    # pylint: disable=unused-argument
    def console_initialize(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: initialize
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        response:typing.Union[dict[str,typing.Any],None] = self.client.command("initialize",data)
        self.client.close()
        if response is None:
            print("Returned empty response")
            return False
        if not response["result"]["state"]:
            print("Failed to initialize new KeyDB; " + (', '.join(response["result"]["messages"])))
            return False
        print_console_initialization_data(response)
        return True

    def console_rotate(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: rotate
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        data["num_keys"] = int(data["num_keys"])
        response:typing.Union[dict[str,typing.Any],None] = self.client.command("rotate",data)
        self.client.close()
        if response is None:
            print("Returned empty response")
            return False
        if not response["result"]["state"]:
            print("Failed to Rotate KeyDB; " + (', '.join(response["result"]["messages"])))
            return False
        output_rows:list[list[str]] = [["Keys"]]
        for k in response["keys"]:
            output_rows.append([k])
        notice:list[list[str]] = [
            ["WARNING: KeyDB unlock keys have been rotated!!!!"]
        ]
        notice += self._KEYDB_NOTICE
        print(tabulate(notice,tablefmt="outline"))
        print(tabulate(output_rows,headers="firstrow",tablefmt="outline"))
        return True

    def console_status(self,_:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: status
        @param dict[str,Any] \c data Request data object; Unused
        @retval bool Command Success/Failure
        """
        response:dict[str,bool] = self.client.status()
        self.client.close()
        initialized:str = "Yes" if response["initialized"] else "No"
        unlocked:str = "No" if response["locked"] else "Yes"
        print(f"Initialized: {initialized}")
        print(f"Unlocked: {unlocked}")
        return True

    def console_deauth(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: deauth
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        result:bool = self.client.deauth()
        self.client.close()
        if not result:
            self.logger.error("Deauth Failed, See other messages, on client and server")
            return False
        print("Deauthorized")
        if data["have_auth_file"]:
            input_type:str = data["input_type"]
            if input_type == "auto":
                input_type = "toml"
            auth_path:Path = Path(data["auth_file"]).expanduser().resolve()
            auth_path_str:str = auth_path.as_posix()
            auth_file_data:dict[str,typing.Any] = UtilFuncs.load_sfile(auth_path,input_type)
            auth_file_data.pop("auth_token")
            with open(auth_path, "w", encoding="utf-8") as f:
                f.write(UtilFuncs.dump_sstr(auth_file_data,input_type))
            auth_path.chmod(0o600)
            print(f"Removed Auth Token from {auth_path_str}")
        return result

    def console_authorize(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: authorize
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        result:bool = self.client.authorize(access_key_id=data["access_key_id"],private_key=Path(data["private_key"]),key_password=data["key_password"],expire_time=data["expire_time"])
        self.client.close()
        if not result:
            self.logger.error("Authorization Failed, See other messages, on client and server")
            return False
        print("Authorization Success")
        if data["have_auth_file"]:
            input_type:str = data["input_type"]
            if input_type == "auto":
                input_type = "toml"
            auth_path:Path = Path(data["auth_file"]).expanduser().resolve()
            auth_path_str:str = auth_path.as_posix()
            auth_file_data:dict[str,typing.Any] = UtilFuncs.load_sfile(auth_path,input_type)
            auth_file_data["auth_token"] = self.client.get_auth_token()
            with open(auth_path, "w", encoding="utf-8") as f:
                f.write(UtilFuncs.dump_sstr(auth_file_data,input_type))
            auth_path.chmod(0o600)
            print(f"Wrote Auth Token to {auth_path_str}")
        else:
            print(f"AuthToken: {self.client.get_auth_token()}")
        return True

    def console_list_groups(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: list_groups
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        response:list[str] = self.client.list_groups()
        self.client.close()
        print("Groups:")
        for g in response:
            print(f"\t{g}")
        return True

    def console_list_users(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: list_users
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        response:list[str] = self.client.list_users()
        self.client.close()
        print("Users:")
        for u in response:
            print(f"\t{u}")
        return True

    def console_list_acls(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: list_acls
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        response:list[str] = self.client.list_acls()
        self.client.close()
        print("ACLs:")
        for a in response:
            print(f"\t{a}")
        return True

    def console_list_keysets(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: list_keysets
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        response:list[str] = self.client.list_keysets()
        self.client.close()
        print("Keysets:")
        for a in response:
            print(f"\t{a}")
        return True

    def console_list_stores(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: list_stores
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        response:list[str] = self.client.list_stores()
        self.client.close()
        print("Secrets Stores:")
        for a in response:
            print(f"\t{a}")
        return True

    def console_list_store_types(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: list_store_types
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        response:list[str] = self.client.list_store_types()
        self.client.close()
        print("Secrets Store Types:")
        for a in response:
            print(f"\t{a}")
        return True

    def console_command_list(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: command_list
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        resp:typing.Union[dict[str,typing.Any],None] = self.client.command("command_list")
        self.client.close()
        if resp is None:
            print("Returned Empty Response")
            return False
        print("Commands:",end="\n\t")
        i:int = 0
        for command in resp["commands"]:
            command_config:argstruct.ArgStructCommand = self._argstruct.commands[command]
            if command_config.get("cli_hidden"):
                continue
            i += 1
            if i == 5:
                i = 0
                end = "\n\t"
            else:
                end = ", "
            print(command,end=end)
        print("")
        return True

    def console_create_user(self,data:dict[str,typing.Any]) -> bool:
        """Console Output; COMMAND: create_user
        @param dict[str,Any] \c data Request data object
        @retval bool Command Success/Failure
        """
        user:str = data["user_name"]
        if data["public_key"].startswith("@"):
            data["public_key"] = Path(data["public_key"].lstrip("@"))
        access_key_id:str = self.client.create_user(user_name=user,public_key=data["public_key"])
        self.client.close()
        print(f"Created User '{user}'")
        print(f"Access Key ID: {access_key_id}")
        return True
    # pylint: enable=unused-argument

    def command(self,command:str,data:typing.Union[dict[str,typing.Any],None] = None) -> bool:
        """Console Operator ('Any' Command)
        @param dict[str,Any] \c call_args Commandline Arguments
        @retval bool Success/Failure
        """
        if data is None:
            raise ValueError("Console Commands require some form of data")
        # if command in [ "service-stop", "stop" ]:
        #     self._service_stop()
        #     return True
        if command not in self._argstruct.commands.keys():
            raise RuntimeError("Invalid Command")
        console_actions:dict[str,typing.Callable] = get_actions(self)
        self.client.connect()
        if not self.client.connected:
            self.logger.error("Unable to connect to server. See previous errors")
            sys_exit(1)
        if "auth_token" in data.keys():
            self.client.set_auth_token(data["access_key_id"],data["auth_token"])
        if command not in [ "authorize", "deauth" ]:
            for k in [ "have_auth_file", "auth_file", "auth_token", "access_key_id", "private_key", "key_password" ]:
                if k in data.keys():
                    data.pop(k)
        command_action:typing.Callable
        result:bool = False
        if f"console_{command}" in console_actions.keys():
            command_action = console_actions[f"console_{command}"]
            result = command_action(data)
        else:
            response:typing.Union[dict[str,typing.Any],None] = self.client.command(command,data)
            result = self._dump_result_to_console(response)
        try:
            self.client.close()
        except BrokenPipeError:
            pass
        return result

    def _dump_result_to_console(self,response:typing.Union[dict[str,typing.Any],None]) -> bool:
        """Generic Console Output
        @param dict[str,Any] \c response API Response object
        @retval None Nothing
        """
        if response is None:
            return True
        result:bool = response["result"]["state"]
        result_str:str = "Success" if result else "Failure"
        print(f"Result: {result_str}")
        if len(response["result"]["messages"]) > 0:
            print("Message(s):")
            for m in response["result"]["messages"]:
                print(f"\t{m}")
        response.pop("result")
        if len(response) > 0:
            print(json.dumps(response,indent=4))
        return result

    # def _service_stop(self) -> None:
    #     """COMMAND; Request Secrets Manager Service Stop
    #     Only to be run from system where Secrets Manager Service is running
    #     """
    #     service_name:str = "convection-secrets"
    #     shutdown_limit:int = 300
    #     pid_dir:Path
    #     try:
    #         pid_dir = Path(self.client.get_configuration_value("pid_dir",False)).resolve()
    #     except ValueError:
    #         pid_dir = Path(f"/var/run/{service_name}/")
    #     pid_file:Path = pid_dir.joinpath(f"{service_name}.pid")
    #     if pid_file.is_file():
    #         with open(pid_file, "r", encoding="utf-8") as f:
    #             pid:int = int(f.read())
    #         if UtilFuncs.check_pid(pid):
    #             self.client.connect()
    #             if not self.client.connected:
    #                 self.logger.error("Unable to connect to server. See previous errors")
    #                 sys_exit(1)
    #             response:typing.Union[dict[str,typing.Any],None] = self.client.command("service-stop")
    #             self.client.close()
    #             if response is None:
    #                 self.logger.warning("Service returned no data")
    #                 sys_exit(1)
    #             else:
    #                 self.logger.info(f"Waiting for process {str(pid)} to end")
    #                 wait:int = 0
    #                 while pid_file.is_file():
    #                     if wait >= shutdown_limit:
    #                         self.logger.error(f"Timed out waiting for process {str(pid)} to end")
    #                         sys_exit(4)
    #                     sleep(1)
    #                     wait += 1
    #                 self.logger.info("Service Stopped")
    #                 sys_exit(0)
    #         else:
    #             self.logger.warning(f"Process {str(pid)} was not running")
    #             sys_exit(2)
    #     else:
    #         self.logger.warning("Service was not running on this system")
    #         self.logger.error("This command is only meant to be called from the system hosting Convection Secret Manager")
    #         sys_exit(1)

def console_secrets_run(input_args:dict[str,typing.Any]) -> None:
    """Secrets Command Processing
    @param dict[str,Any] \c input_args Commandline Input Args
    @retval None Nothing
    """
    if input_args["sub_command"] in [ "initialize", "service-start", "start", "service-stop", "stop", "default_config" ] :
        print("This command can only be run from the Convection Secrets Server-side Client, this is not the Server-side Client")
        sys_exit(1)
    input_args["have_auth_file"] = False
    if "auth_file" in input_args.keys():
        if input_args["auth_file"] is not None:
            auth_path:Path = Path(input_args["auth_file"]).expanduser().resolve()
            auth_path_str:str = auth_path.as_posix()
            if auth_path.is_file():
                input_args["auth_file"] = auth_path_str
                raw_auth_data:dict[str,typing.Any] = UtilFuncs.load_sfile(auth_path,input_args["input_type"])
                auth_data_keys:list[str] = list(raw_auth_data.keys())
                allowed_keys:list[str] = [ "public_key", "private_key", "access_key_id", "auth_token", "key_password" ]
                for k in auth_data_keys:
                    if k in allowed_keys:
                        input_args[k] = raw_auth_data[k]
                input_args["have_auth_file"] = True
            else:
                print(f"Cannot locate {auth_path_str}")
    input_args["config_prefix"] = "global.secrets.client"
    input_args["specker_root"] = "secrets-console"
    secrets_client:ConvectionSecretsConsole = ConvectionSecretsConsole(input_args)
    command:str = input_args.pop("sub_command")
    result:bool = False
    try:
        result = secrets_client.command(command,input_args)
    except RuntimeError:
        print("Invalid Command")
        exit_invalid_cmd()
    r:int = 0 if result else 1
    sys_exit(r)

def secrets_client_bin() -> None:
    """Convection Secrets Manager Main Execution
    """
    parser:argparse.ArgumentParser = argparse.ArgumentParser(description="Convection SM - Convection Secrets Manager")
    parser.add_argument("-v","--verbose",help="Turn on Debugging",action="store_true")
    parser.add_argument("-c","--config",help="Path to main config file")
    parser.add_argument("-t","--input-type",help="Force override of input type",choices=get_config_types(True),default="auto")
    parser.add_argument("--specker_debug",help="Turn on Debugging for Specker Specs",action="store_true")
    parser.add_argument("--sensitive_debug",help="Enable Sensitve Data Display/Logging for Debugging\n\t\t\tWARNING: DANGEROUS",action="store_true")

    shared_path:Path = Path(importlib.import_module("convection.shared").__path__[0]).resolve()
    m_path:Path = shared_path.joinpath("convection-sm-commands.toml")
    spec_path:Path = shared_path.joinpath("specs/")
    argstruct_obj:argstruct.ArgStruct = argstruct.ArgStruct(m_path,"toml",[spec_path])
    argstruct.console(argstruct_obj,parser,True,{ "dest": "sub_command", "required": True })
    input_args:typing.Union[dict[typing.Any,typing.Any],None] = vars(parser.parse_args())
    if input_args is None:
        parser.print_help()
        sys_exit(1)

    # pylint: disable=duplicate-code
    loglevel:int = logging.WARNING
    if input_args["verbose"]:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel,format="%(levelname)s \t%(threadName)s\t%(module)s \t%(message)s")
    input_args["loglevel"] = loglevel
    # pylint: enable=duplicate-code
    old_paths:list[Path] = UtilFuncs.CONFIG_SCAN_BASE_PATHS
    for c_name,f_name in { "config": "convection-secrets.client", "auth_file": "convection-secrets.auth" }.items():
        if c_name not in input_args.keys() or input_args[c_name] is None:
            UtilFuncs.add_config_search_path(Path(os.getcwd()))
            file_path:typing.Union[Path,None] = UtilFuncs.find_config_file("",f_name)
            if file_path is None:
                logging.warning(f"NO CONFIG for {f_name}")
                continue
            file_path_str:str = file_path.as_posix()
            logging.debug(f"Using {c_name} {file_path_str}")
            input_args[c_name] = file_path_str
    UtilFuncs.CONFIG_SCAN_BASE_PATHS = old_paths
    console_secrets_run(input_args)
