# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import typing
from pathlib import Path
from convection.secrets.client.api.core import SecretsClientMethodsCore

from convection.secrets.client.api.core import SecretsClientMethodsCore

class SecretsClientUserMethods(SecretsClientMethodsCore):

    # Pylint Unused Argument flag is disabled for a majority of the Client Commands due to usage
    #  of `locals()`, linting doesnt catch that its used and so flags args as unused.
    # pylint: disable=unused-argument
    def audit_user(self,user_name:str) -> dict[str,typing.Any]:
        """Get User Information
        @param str \c user_name Username to get info on
        @retval dict[str,Any] User data. ACLs User has attached (includes group ACLs), Groups that user is a part of, Number of Access Keys and Number of Auth Tokens
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("audit_user",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        response.pop("result")
        return response

    def list_users(self) -> list[str]:
        """User List
        @retval list[str] List of Registered Usernames
        """
        response:typing.Union[dict[str,typing.Any],None] = self.command("list_users",None)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        result:bool = response["result"]["state"]
        if not result:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return list[str](response["users"])

    def create_user(self,user_name:str, public_key:typing.Union[Path,str]) -> str:
        """User Creation / Access Key Generation
        @param str \c username Username, created if does not exist
        @param Union[Path,str] public_key Public Key. If String, must be the content of the public key (not the path, use pathlib.Path to reference the file)
        @retval New Access Key ID
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        pubkey_data:str = ""
        if isinstance(public_key,str):
            self.logger.debug("Public Key was directly provided (not a file)")
            pubkey_data = public_key
        else:
            pubkey_path:Path = public_key.expanduser().resolve()
            if not pubkey_path.is_file():
                public_key_str:str = public_key.as_posix()
                raise FileNotFoundError(f"No Such Public Key {public_key_str}")
            with open(pubkey_path.resolve(),"r",encoding="utf-8") as f:
                pubkey_data = f.read()
        data["public_key"] = pubkey_data
        response:typing.Union[dict[str,typing.Any],None] = self.command("create_user",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return str(response["access_key_id"])

    def remove_access(self,user_name:typing.Union[str,None] = None, remove_access_key_id:typing.Union[str,None] = None, remove_public_key:typing.Union[str,None] = None) -> bool:
        """Remove a User or Access Key ID / Public Key
        @param Union[str,None] \c user_name User name to operate on (if other fields filled), otherwise, User to delete completely
        @param Union[str,None] \c remove_access_key_id Access Key ID to remove
        @param Union[str,None] \c remove_public_key Public Key to search for, and remove associated Access Key ID, if found
        @retval bool Success/Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        if len(data) == 0:
            raise RuntimeError("At least one parameter of `remove_access` must be filled")
        response:typing.Union[dict[str,typing.Any],None] = self.command("remove_access",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])
    # pylint: enable=unused-argument
