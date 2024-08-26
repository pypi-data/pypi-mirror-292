# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

from convection.secrets.client.api.core import SecretsClientMethodsCore

class SecretsClientKeyMethods(SecretsClientMethodsCore):

    # Pylint Unused Argument flag is disabled for a majority of the Client Commands due to usage
    #  of `locals()`, linting doesnt catch that its used and so flags args as unused.
    # pylint: disable=unused-argument
    def create_keyset(self,keyset_name:str) -> bool:
        """Create new KeySet
        @param str \c keyset_name Name of KeySet to create, Must be unique
        @retval bool Creation Success/Failure
        """
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("create_keyset",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return bool(response["result"]["state"])

    def list_keysets(self) -> list[str]:
        """List Registered KeySets
        @retval list[str] List of KeySet Names
        """
        response:typing.Union[dict[str,typing.Any],None] = self.command("list_keysets")
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return list[str](response["keysets"])
    # pylint: enable=unused-argument