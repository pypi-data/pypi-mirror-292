# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import typing
import base64
from pathlib import Path
from uuid import UUID
from convection.secrets.client.api.core import SecretsClientMethodsCore

from cryptography.hazmat.backends import default_backend

# Older Cryptography libraries less than v42.0 had RSAPrivateKey hidden behind the backends
# Newer versions (v42.0+) now have it available in the asymmetric.rsa module
try:
    from cryptography.hazmat.backends.openssl.rsa import _RSAPrivateKey as PrivateKey
except ModuleNotFoundError:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey as PrivateKey

from cryptography.hazmat.primitives.serialization import load_der_private_key,load_pem_private_key
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.asymmetric.padding import OAEP,MGF1

import argstruct

from convection.shared.exceptions import AuthenticationError, InvalidPrivateKeyError
from convection.secrets.client.api.core import SecretsClientMethodsCore

class SecretsClientAuthMethods(SecretsClientMethodsCore):
    _access_key_id:typing.Union[str,None]
    _auth_token:typing.Union[str,None]

    def get_access_key_id(self) -> typing.Union[str,None]:
        """Get Raw Access Key ID (SECURITY HAZARD)
        @retval Union[str,None] Access Key ID that has been set. None if not set
        """
        return self._access_key_id

    def get_auth_token(self) -> typing.Union[str,None]:
        """Get Raw Auth Token (SECURITY HAZARD)
        @retval Union[str,None] Auth Token that has been set or gotten from authorize command. None if not set
        """
        return self._auth_token

    def set_auth_token(self,access_key_id:str, auth_token:str) -> None:
        """Set Access Key and Auth Token to pre-specified value
        @param str \c access_key_id Access Key ID
        @param str \c auth_token Auth Token
        @retval None Nothing
        """
        self._access_key_id = access_key_id
        self._auth_token = auth_token

    def deauth(self) -> bool:
        """Deauth / Logout Call
        @param str \c access_key_id Access Key ID
        @param str \c auth_token Auth Token
        @retval bool Deauth Result (False )
        """
        if self._access_key_id is None or self._auth_token is None:
            self.logger.error("Not Authenticated")
            raise AuthenticationError()
        self.connect()
        if not self.connected or self._connection is None:
            self.logger.error("Unable to connect to server. See previous errors")
            raise ConnectionError("Unable to connect to server. See previous errors")
        data:dict[str,typing.Any] = {}
        self._send_command("deauth",self._attach_auth_data(data))
        response:typing.Union[dict[str,typing.Any],None] = self._read_result()
        self._access_key_id = None
        self._auth_token = None
        if response is None:
            self.logger.warning("Got Empty Response from Server")
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            return False
        return True

    def authorize(self,access_key_id:str,private_key:typing.Union[Path,str],key_password:typing.Union[str,None] = None, expire_time:typing.Union[str,None] = None) -> bool:
        """Command Authorization Call
        @param str access_key_id Access Key ID
        @param Union[Path,str] private_key Private Key. If String, must be the content of the private key (not the path, use pathlib.Path to reference the file)
        @param bool close_connection Whether or not to close connection when completed
        @retval Union[dict[str,Any],None] Response Data, may be None
        @raises InvalidPrivateKeyError Invalid Private Key Format (Not PEM/DER)
        @raises InvalidPrivateKeyError Provided Private Key was unable to decrypt token (Wrong Private Key)
        """
        self.connect()
        if not self.connected or self._connection is None:
            self.logger.error("Unable to connect to server. See previous errors")
            raise ConnectionError("Unable to connect to server. See previous errors")
        data:typing.Union[dict[str,typing.Any],None] = { "access_key_id": access_key_id, "expire_time": expire_time, "command": "authorize" }
        data = argstruct.parse(self._argstruct,data,"command")
        data.pop("command") # type: ignore
        self._send_command("authorize",data)
        response:typing.Union[dict[str,typing.Any],None] = self._read_result()
        if response is None:
            self.logger.error("Authorization Failed, Server returned empty Result")
            return False
        if not response["result"]["state"]:
            self.logger.error("Authorization Failed, Result was False")
            self.logger.error(', '.join(response["result"]["messages"]))
            return False
        token_id:str = UUID(bytes=self._private_key_decrypt(private_key,response["response"],key_password)).hex
        self._connection.send(bytes(token_id,"utf-8"))
        response = self._read_result()
        if response is None:
            self.logger.warning("Got Empty Response from Server")
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            return False
        self.logger.info("Authenticated!")
        self._access_key_id = access_key_id
        self._auth_token = token_id
        return True

    def _private_key_decrypt(self,private_key:typing.Union[Path,str],content:str,key_password:typing.Union[str,None] = None) -> bytes:
        """Decrypt Encrypted data
        @param Union[Path,str] \c private_key Path to private key (as Path only) or private key content (including header and footer)
        @param str \c content Encrypted content to decrypt
        @param Union[str,None] \c key_password Private Key password, default None
        @retval bytes Decrypted data as bytes
        """
        privkey_data:str = ""
        if isinstance(private_key,Path):
            with open(private_key.expanduser().resolve(),"r",encoding="utf-8") as f:
                privkey_data = f.read()
        else:
            privkey_data = private_key
        privkey_fixed:str = '\n'.join([ p for p in privkey_data.split('\n') if not p.startswith("-----") ])
        priv_obj:PrivateKey
        try:
            priv_obj = load_der_private_key(base64.b64decode(privkey_fixed),backend=default_backend(),password=key_password) # type: ignore
        except ValueError:
            self.logger.debug("Private Key was not a DER format, attempting PEM")
            try:
                priv_obj = load_pem_private_key(base64.b64decode(privkey_fixed),backend=default_backend(),password=key_password) # type: ignore
            except ValueError as e:
                self.logger.debug("Private Key was not a PEM format either, bailing out")
                self.logger.error(f"Unable to load Private Key, {e}")
                raise InvalidPrivateKeyError() from e
        try:
            result:bytes = priv_obj.decrypt(
                base64.b64decode(content),
                OAEP(
                    mgf=MGF1(algorithm=SHA512()),
                    algorithm=SHA512(),
                    label=None
                )
            )
        except ValueError as e:
            self.logger.info("Decryption Failed. Private Key does not match Access Key ID")
            raise InvalidPrivateKeyError(e) from e
        return result
    # pylint: enable=unused-argument