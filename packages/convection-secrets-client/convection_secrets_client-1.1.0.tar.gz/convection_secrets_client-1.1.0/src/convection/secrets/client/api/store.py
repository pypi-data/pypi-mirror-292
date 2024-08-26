# Copyright 2023-2024 by AccidentallyTheCable <cableninja@cableninja.net>.
# All rights reserved.
# This file is part of Convection Secrets Client,
# and is released under "GPLv3". Please see the LICENSE
# file that should have been included as part of this package.
#### END COPYRIGHT BLOCK ###
import typing

from convection.secrets.client.api.core import SecretsClientMethodsCore

class SecretsClientStoreMethods(SecretsClientMethodsCore):

    # Pylint Unused Argument flag is disabled for a majority of the Client Commands due to usage
    #  of `locals()`, linting doesnt catch that its used and so flags args as unused.
    # pylint: disable=unused-argument
    def list_stores(self) -> list[str]:
        """List Registered Secrets Stores
        @retval list[str] List of Secrets Stores
        """
        response:typing.Union[dict[str,typing.Any],None] = self.command("list_stores")
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return list[str](response["stores"])

    def list_store_types(self) -> list[str]:
        """List Secrets Store Types
        @retval list[str] List of Secrets Store Types
        """
        response:typing.Union[dict[str,typing.Any],None] = self.command("list_store_types")
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        return list[str](response["store_types"])

    def store_info(self,store_name:str) -> dict[str,typing.Any]:
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("store_info",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        response.pop("result")
        return response

    def store_config(self,store_name:str,store_config:dict[str,typing.Any]) -> typing.Any:
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("store_config",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        response.pop("result")
        return response

    def create_store(self,store_name:str,keyset_name:str,store_type_name:str,store_args:typing.Union[dict[str,typing.Any],None]) -> bool:
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("create_store",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        result:bool = response["result"]["state"]
        return result

    def remove_store(self,store_name:str) -> bool:
        data:dict[str,typing.Any] = locals()
        data.pop("self")
        response:typing.Union[dict[str,typing.Any],None] = self.command("remove_store",data)
        if response is None:
            raise RuntimeError("Command returned an empty response")
        if not response["result"]["state"]:
            response_messages:str = '; '.join(response["result"]["messages"])
            self.logger.error(f"Command Failed. {response_messages}")
            raise RuntimeError(response_messages)
        result:bool = response["result"]["state"]
        return result

    # pylint: enable=unused-argument
