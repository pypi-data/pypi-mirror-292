# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import typing
from convection.secrets.client.api.core import SecretsClientMethodsCore

from convection.secrets.client.api.core import SecretsClientMethodsCore

class SecretsClientGroupMethods(SecretsClientMethodsCore):

    # Pylint Unused Argument flag is disabled for a majority of the Client Commands due to usage
    #  of `locals()`, linting doesnt catch that its used and so flags args as unused.
    # pylint: disable=unused-argument
    def audit_group(self,group_name:str) -> dict[str,typing.Any]:
        """Get Group Information
        @param str \c group_name Group Name to get info on
        @retval dict[str,Any] Group Data. ACLs that Group has attached, List of Users in Group
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("audit_group",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        response.pop("result")
        return response

    def list_groups(self) -> list[str]:
        """Group List
        @retval list[dict[str,typing.Any]] List of Registered Groups
        """
        response:typing.Union[dict[str,typing.Any],None] = self.command("list_groups",None)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        result:bool = response["result"]["state"]
        if not result:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return list[str](response["groups"])

    def create_group(self,group_name:str) -> bool:
        """Group Create
        @param str \c group_name Name of Group to create (must be unique)
        @retval bool Success / Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("create_group",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])

    def attach_group(self,group_name:str,user_name:str) -> bool:
        """Attach Group to User
        @param str \c group_name Name of Group to attach to User
        @param str \c user_name Name of User to attach Group to
        @retval bool Success/Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("attach_group",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])

    def detach_group(self,group_name:str,user_name:str) -> bool:
        """Detach Group from User
        @param str \c group_name Name of Group to detach from User
        @param str \c user_name Name of User to detach Group from
        @retval bool Success/Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("detach_group",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])

    def remove_group(self,group_name:str) -> bool:
        """Delete/Remove Group
        @param str \c group_name Name of Group to delete
        @retval bool Success/Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("remove_group",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])
    # pylint: enable=unused-argument
