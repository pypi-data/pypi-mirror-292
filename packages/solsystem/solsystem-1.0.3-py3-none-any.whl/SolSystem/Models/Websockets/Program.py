from __future__ import annotations
from typing import Any
from pydantic import model_serializer

from SolSystem.Models.Accounts.Filters import Filter
from SolSystem.Models.Accounts.Account import ProgramAccount
from SolSystem.Models.Common import (
    WsMethod,
    WsResponse,
    PublicKey,
    WsMethodName,
    Configuration,
    MethodMetadata,
    ConfigurationField,
)



class WsGetProgram(WsMethod[WsResponse[ProgramAccount]]):
    program: PublicKey
    filters: list[Filter] | None

    def __init__(
            self,
            program: PublicKey,
            filters: list[Filter] | None = None, 
            configuration: Configuration | None = None,
        ) -> None:
        """### Summary
        Recieve a notification when the lamports or data for an account owned
        by the given program changes
        
        ### Parameters
        `program:` Public key of program

        `filters:` Filter results using up Filter objects. All filters must pass
        to recieve the result.

        #### Configuration Parameters Accepted:
        `encoding`, `commitment`"""
        if not configuration:
            configuration = Configuration()

        configuration.filter_for_accepted_parameters([
            ConfigurationField.ENCODING,
            ConfigurationField.COMMITMENT,
        ])
        super().__init__(
            response_type = WsResponse[ProgramAccount],
            metadata = MethodMetadata[WsMethodName](method = WsMethodName.PROGRAM),
            configuration = configuration,
            program = program, # type:ignore
            filters = filters, # type:ignore
        )


    @model_serializer
    def request_serializer(self) -> dict[str, Any]:
        request = self.metadata.model_dump()
        parameters: list[Any] = [self.program]
        
        return { **request, "params": self.add_configuration(parameters) }
