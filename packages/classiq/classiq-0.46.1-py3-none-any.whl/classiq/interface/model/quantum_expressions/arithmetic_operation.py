from typing import Dict, Literal, Mapping, Sequence

import pydantic

from classiq.interface.generator.arith.arithmetic import (
    ARITHMETIC_EXPRESSION_RESULT_NAME,
    compute_arithmetic_result_type,
)
from classiq.interface.model.handle_binding import (
    ConcreteHandleBinding,
    HandleBinding,
)
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumAssignmentOperation,
)
from classiq.interface.model.quantum_statement import HandleMetadata
from classiq.interface.model.quantum_type import QuantumType


class ArithmeticOperation(QuantumAssignmentOperation):
    kind: Literal["ArithmeticOperation"]

    inplace_result: bool = pydantic.Field(
        description="Determines whether the result variable is initialized",
    )

    def initialize_var_types(
        self,
        var_types: Dict[str, QuantumType],
        machine_precision: int,
    ) -> None:
        super().initialize_var_types(var_types, machine_precision)
        self._result_type = compute_arithmetic_result_type(
            self.expression.expr, var_types, machine_precision
        )

    @property
    def wiring_inouts(
        self,
    ) -> Mapping[str, ConcreteHandleBinding]:
        inouts = dict(super().wiring_inouts)
        if self.inplace_result:
            inouts[self.result_name()] = self.result_var
        return inouts

    @property
    def readable_inouts(self) -> Sequence[HandleMetadata]:
        inouts = [
            HandleMetadata(handle=handle, readable_location="in an expression")
            for handle in self.var_handles
        ]
        if self.inplace_result:
            inouts.append(
                HandleMetadata(
                    handle=self.result_var,
                    readable_location="on the left-hand side of an in-place assignment",
                )
            )
        return inouts

    @property
    def wiring_outputs(self) -> Mapping[str, HandleBinding]:
        if self.inplace_result:
            return {}
        return super().wiring_outputs

    @property
    def readable_outputs(self) -> Sequence[HandleMetadata]:
        if self.inplace_result:
            return []
        return [
            HandleMetadata(
                handle=self.result_var,
                readable_location="on the left-hand side of an assignment",
            )
        ]

    @classmethod
    def result_name(cls) -> str:
        return ARITHMETIC_EXPRESSION_RESULT_NAME
