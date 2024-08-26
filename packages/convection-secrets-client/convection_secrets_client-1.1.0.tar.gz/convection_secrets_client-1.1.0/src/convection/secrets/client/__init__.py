# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###

import typing
from convection.secrets.client.api.acl import SecretsClientACLMethods
from convection.secrets.client.api.auth import SecretsClientAuthMethods
from convection.secrets.client.api.core import SecretsClientMethodsCore
from convection.secrets.client.api.group import SecretsClientGroupMethods
from convection.secrets.client.api.keys import SecretsClientKeyMethods
from convection.secrets.client.api.secrets import SecretsClientSecretsMethods
from convection.secrets.client.api.store import SecretsClientStoreMethods
from convection.secrets.client.api.user import SecretsClientUserMethods

class ConvectionSecretsClient(
        SecretsClientUserMethods,SecretsClientGroupMethods,
        SecretsClientACLMethods,SecretsClientKeyMethods,
        SecretsClientAuthMethods,SecretsClientStoreMethods,
        SecretsClientSecretsMethods,
        SecretsClientMethodsCore
    ):
    """Convection Secrets Client
    """

    def status(self) -> dict[str,bool]:
        """System Information Request
        @retval dict[str,bool] Status Name, State
        """
        response:typing.Union[dict[str,typing.Any],None] = self.command("status")
        if response is None:
            raise RuntimeError("Command returned an empty response")
        response.pop("result")
        return response

    def command_list(self) -> list[str]:
        """List of Commands available to authenticated user
        @retval list[str] List of commands as strings
        """
        response:typing.Union[dict[str,typing.Any],None] = self.command("command_list")
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return list[str](response["commands"])
