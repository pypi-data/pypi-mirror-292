from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple

from classiq.interface.exceptions import ClassiqInternalExpansionError
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.model.bind_operation import BindOperation
from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.inplace_binary_operation import (
    BinaryOperation,
    InplaceBinaryOperation,
)
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    NamedParamsQuantumFunctionDeclaration,
)
from classiq.interface.model.quantum_statement import QuantumStatement
from classiq.interface.model.quantum_type import (
    QuantumBit,
    QuantumBitvector,
    QuantumNumeric,
)
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)

from classiq.model_expansions.closure import FunctionClosure
from classiq.model_expansions.evaluators.parameter_types import (
    evaluate_types_in_quantum_symbols,
)
from classiq.model_expansions.evaluators.quantum_type_utils import (
    validate_inplace_binary_op_vars,
)
from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import QuantumSymbol, Scope
from classiq.qmod.builtins.functions import integer_xor, modular_add


def _binary_function_declaration(
    op: BinaryOperation,
) -> NamedParamsQuantumFunctionDeclaration:
    return {
        BinaryOperation.Addition: modular_add.func_decl,
        BinaryOperation.Xor: integer_xor.func_decl,
    }[op]


class InplaceBinaryOperationEmitter(Emitter[InplaceBinaryOperation]):
    def emit(self, op: InplaceBinaryOperation, /) -> None:
        value_var = self._interpreter.evaluate(op.value).as_type(QuantumSymbol)
        target_var = self._interpreter.evaluate(op.target).as_type(QuantumSymbol)
        value_var, target_var = evaluate_types_in_quantum_symbols(
            [value_var, target_var], self._current_scope
        )
        validate_inplace_binary_op_vars(value_var, target_var, op.operation.value)
        if TYPE_CHECKING:
            assert isinstance(value_var.quantum_type, QuantumNumeric)
            assert isinstance(target_var.quantum_type, QuantumNumeric)

        sign_diff = int(value_var.quantum_type.sign_value) - int(
            target_var.quantum_type.sign_value
        )
        frac_digits_diff = (
            value_var.quantum_type.fraction_digits_value
            - target_var.quantum_type.fraction_digits_value
        )
        if (
            sign_diff + frac_digits_diff == value_var.quantum_type.size_in_bits
            or -sign_diff - frac_digits_diff == target_var.quantum_type.size_in_bits
        ):
            with self._propagated_var_stack.capture_variables(op):
                return

        value_var = QuantumSymbol(
            handle=HandleBinding(name="value"), quantum_type=value_var.quantum_type
        )
        target_var = QuantumSymbol(
            handle=HandleBinding(name="target"),
            quantum_type=target_var.quantum_type,
        )
        inplace_binary_op_function = FunctionClosure.create(
            name=op.operation.value,
            positional_arg_declarations=[
                PortDeclaration(
                    name=value_var.handle.name,
                    quantum_type=value_var.quantum_type,
                    direction=PortDeclarationDirection.Inout,
                ),
                PortDeclaration(
                    name=target_var.handle.name,
                    quantum_type=target_var.quantum_type,
                    direction=PortDeclarationDirection.Inout,
                ),
            ],
            body=_build_inplace_binary_operation(
                value_var=value_var,
                target_var=target_var,
                frac_digits_diff=frac_digits_diff,
                internal_function_declaration=_binary_function_declaration(
                    op.operation
                ),
            ),
            scope=Scope(parent=self._current_scope),
        )
        with self._propagated_var_stack.capture_variables(op):
            self._emit_quantum_function_call(
                inplace_binary_op_function, [op.value, op.target]
            )


def _build_inplace_binary_operation(
    value_var: QuantumSymbol,
    target_var: QuantumSymbol,
    frac_digits_diff: int,
    internal_function_declaration: NamedParamsQuantumFunctionDeclaration,
) -> List[QuantumStatement]:
    if TYPE_CHECKING:
        assert isinstance(value_var.quantum_type, QuantumNumeric)
        assert isinstance(target_var.quantum_type, QuantumNumeric)

    value_overlap_var, value_sign_var, value_bind_targets = _get_inplace_bind_targets(
        "value", value_var, frac_digits_diff
    )
    target_overlap_var, target_sign_var, target_bind_targets = (
        _get_inplace_bind_targets("target", target_var, -frac_digits_diff)
    )

    value_pre_ops, value_post_ops = _get_inplace_pre_post_ops(
        value_var, value_bind_targets
    )
    target_pre_ops, target_post_ops = _get_inplace_pre_post_ops(
        target_var, target_bind_targets
    )

    binary_ops = []
    if value_overlap_var is not None and target_overlap_var is not None:
        binary_ops.append(
            _internal_inplace_binary_operation_function_call(
                internal_function_declaration,
                value_overlap_var.handle,
                target_overlap_var.handle,
            )
        )
    if value_sign_var is not None and target_sign_var is not None:
        binary_ops.append(
            _internal_inplace_binary_operation_function_call(
                internal_function_declaration,
                value_sign_var.handle,
                target_sign_var.handle,
            )
        )
    if len(binary_ops) == 0:
        raise ClassiqInternalExpansionError("Bug in unrolling inplace operation")

    return [
        *value_pre_ops,
        *target_pre_ops,
        *binary_ops,
        *target_post_ops,
        *value_post_ops,
    ]


def _internal_inplace_binary_operation_function_call(
    internal_function_declaration: NamedParamsQuantumFunctionDeclaration,
    value_var: HandleBinding,
    target_var: HandleBinding,
) -> QuantumFunctionCall:
    internal_function_call = QuantumFunctionCall(
        function=internal_function_declaration.name,
        positional_args=[value_var, target_var],
    )
    internal_function_call.set_func_decl(internal_function_declaration)
    return internal_function_call


def _get_inplace_bind_targets(
    kind: str, var: QuantumSymbol, frac_digits_diff: int
) -> Tuple[Optional[QuantumSymbol], Optional[QuantumSymbol], List[QuantumSymbol]]:
    quantum_type = var.quantum_type
    if TYPE_CHECKING:
        assert isinstance(quantum_type, QuantumNumeric)

    if not quantum_type.sign_value and frac_digits_diff <= 0:
        return var, None, []

    significand_overlap = (
        quantum_type.size_in_bits
        - quantum_type.fraction_digits_value
        - int(quantum_type.sign_value)
    )
    fraction_overlap = quantum_type.fraction_digits_value - max(0, frac_digits_diff)
    if significand_overlap + fraction_overlap == 0 and quantum_type.size_in_bits == 1:
        assert quantum_type.sign_value
        return None, var, []

    bind_targets = []

    if frac_digits_diff > 0:
        bind_targets.append(
            QuantumSymbol(
                handle=HandleBinding(name=f"trimmed_{kind}_fraction_digits"),
                quantum_type=QuantumBitvector(
                    length=Expression(expr=str(frac_digits_diff)),
                ),
            )
        )

    overlap_var = None
    if significand_overlap + fraction_overlap > 0:
        overlap_var = QuantumSymbol(
            handle=HandleBinding(name=f"{kind}_overlap"),
            quantum_type=QuantumNumeric(
                size=Expression(expr=str(significand_overlap + fraction_overlap)),
                is_signed=Expression(expr="False"),
                fraction_digits=Expression(expr=str(fraction_overlap)),
            ),
        )
        bind_targets.append(overlap_var)

    sign_var = None
    if quantum_type.sign_value:
        sign_var = QuantumSymbol(
            handle=HandleBinding(name=f"trimmed_{kind}_sign"),
            quantum_type=QuantumBit(),
        )
        bind_targets.append(sign_var)

    return overlap_var, sign_var, bind_targets


def _get_inplace_pre_post_ops(
    var: QuantumSymbol, bind_targets: List[QuantumSymbol]
) -> Tuple[Sequence[QuantumStatement], Sequence[QuantumStatement]]:
    if len(bind_targets) == 0:
        return [], []

    value_bind_op = BindOperation(
        in_handles=[var.handle],
        out_handles=[var.handle for var in bind_targets],
    )
    return [
        VariableDeclarationStatement(
            name=var.handle.name,
            quantum_type=var.quantum_type,
        )
        for var in bind_targets
    ] + [value_bind_op], [value_bind_op.reversed()]
