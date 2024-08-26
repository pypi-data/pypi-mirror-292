# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import typing
from convection.secrets.client.api.core import SecretsClientMethodsCore

from convection.secrets.client.api.core import SecretsClientMethodsCore

class SecretsClientACLMethods(SecretsClientMethodsCore):
    # Pylint Unused Argument flag is disabled for a majority of the Client Commands due to usage
    #  of `locals()`, linting doesnt catch that its used and so flags args as unused.
    # pylint: disable=unused-argument
    def audit_acl(self,acl_name:str) -> dict[str,typing.Any]:
        """Get ACL Information
        @param str \c acl_name Name of ACL to get info on
        @retval dict[str,Any] ACL Object
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("audit_acl",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        response.pop("result")
        return response

    def list_acls(self) -> list[str]:
        """ACL List
        @retval list[str] List of Registered ACL Names
        """
        response:typing.Union[dict[str,typing.Any],None] = self.command("list_acls",None)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        result:bool = response["result"]["state"]
        if not result:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return list[str](response["acls"])

    def create_acl(self,acl_name:str,mode:int,access_mode:int, acl_type:str, acl_args:typing.Union[dict[str,typing.Any],None] = None) -> bool:
        """Create a new ACL
        @param str \c acl_name Name of ACL to create, must be unique
        @param int \c mode A ConvectionSecretsClient.ACL_MODE_* value
        @param int \c access_mode A ConvectionSecretsClient.ACL_ACCESS_MODE_* value
        @param str \c acl_type A ConvectionSecretsClient.ACL_TYPE_* value
        @param dict[str,Any] \c acl_args ACL Arguments, required keys depend on `acl_type`, see Documentation
        @retval bool Success/Failure
        """
        if acl_args is None:
            acl_args = {}
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        for k,v in acl_args.items():
            data[k] = v
        response:typing.Union[dict[str,typing.Any],None] = self.command("create_acl",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])

    def attach_acl(self,acl_name:str, attach_type:str, attach_name:str) -> bool:
        """Attach ACL to User or Group
        @param str \c acl_name Name of ACL to attach, must exist
        @param str \c attach_type A ConvectionSecretsClient.ATTACH_ACL_* value
        @param str \c attach_name Name of Group or User to attach to
        @retval bool Success/Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("attach_acl",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])

    def detach_acl(self,acl_name:str, detach_type:str, detach_name:str) -> bool:
        """Remove ACL from User or Group
        @param str \c acl_name Name of ACL to detach, must exist
        @param str \c attach_type A ConvectionSecretsClient.ATTACH_ACL_* value
        @param str \c attach_name Name of Group or User to detach from
        @retval bool Success/Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("detach_acl",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])

    def remove_acl(self,acl_name:str) -> bool:
        """Delete/Remove ACL
        @param str \c acl_name Name of ACL to delete
        @retval bool Success\Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("remove_acl",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])
    # pylint: enable=unused-argument
