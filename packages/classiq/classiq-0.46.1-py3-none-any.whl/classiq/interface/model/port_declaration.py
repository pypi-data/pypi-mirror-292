from typing import Any, Dict, Literal, Mapping, Optional

import pydantic

from classiq.interface.exceptions import ClassiqInternalError, ClassiqValueError
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.concrete_types import ConcreteQuantumType
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.helpers.pydantic_model_helpers import values_with_discriminator
from classiq.interface.model.parameter import Parameter
from classiq.interface.model.quantum_variable_declaration import (
    QuantumVariableDeclaration,
)


class AnonPortDeclaration(Parameter):
    kind: Literal["PortDeclaration"]

    quantum_type: ConcreteQuantumType
    size: Optional[Expression] = pydantic.Field(default=None, exclude=True)
    direction: PortDeclarationDirection

    @pydantic.root_validator(pre=True)
    def _set_kind(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        return values_with_discriminator(values, "kind", "PortDeclaration")

    @pydantic.validator("direction")
    def _direction_validator(
        cls, direction: PortDeclarationDirection, values: Mapping[str, Any]
    ) -> PortDeclarationDirection:
        if direction is PortDeclarationDirection.Output:
            quantum_type = values.get("quantum_type")
            if quantum_type is None:
                raise ClassiqValueError("Port declaration is missing a type")

        return direction

    @pydantic.validator("size")
    def _propagate_size_to_type(
        cls, size: Optional[Expression], values: Mapping[str, Any]
    ) -> Optional[Expression]:
        return QuantumVariableDeclaration._propagate_size_to_type(size, values)

    def rename(self, new_name: str) -> "PortDeclaration":
        if type(self) not in (AnonPortDeclaration, PortDeclaration):
            raise ClassiqInternalError
        return PortDeclaration(**{**self.__dict__, "name": new_name})


class PortDeclaration(AnonPortDeclaration):
    name: str
