import inspect
import sys
import warnings
from types import FrameType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Final,
    List,
    Mapping,
    Optional,
    Union,
    overload,
)

from classiq.interface.exceptions import ClassiqValueError
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.builtins.internal_operators import (
    REPEAT_OPERATOR_NAME,
)
from classiq.interface.generator.functions.classical_type import Integer
from classiq.interface.model.bind_operation import BindOperation
from classiq.interface.model.classical_if import ClassicalIf
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.control import Control
from classiq.interface.model.inplace_binary_operation import (
    BinaryOperation,
    InplaceBinaryOperation,
)
from classiq.interface.model.invert import Invert
from classiq.interface.model.power import Power
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_function_declaration import (
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_lambda_function import QuantumLambdaFunction
from classiq.interface.model.repeat import Repeat
from classiq.interface.model.statement_block import StatementBlock
from classiq.interface.model.within_apply_operation import WithinApply

from classiq.qmod.qmod_variable import Input, Output, QArray, QBit, QNum, QVar
from classiq.qmod.quantum_callable import QCallable
from classiq.qmod.quantum_expandable import prepare_arg
from classiq.qmod.symbolic_expr import SymbolicExpr
from classiq.qmod.utilities import get_source_ref

_MISSING_VALUE: Final[int] = -1


def bind(
    source: Union[Input[QVar], List[Input[QVar]]],
    destination: Union[Output[QVar], List[Output[QVar]]],
) -> None:
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    if not isinstance(source, list):
        source = [source]
    if not isinstance(destination, list):
        destination = [destination]
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        BindOperation(
            in_handles=[src_var.get_handle_binding() for src_var in source],
            out_handles=[dst_var.get_handle_binding() for dst_var in destination],
            source_ref=source_ref,
        )
    )


def if_(
    condition: Union[SymbolicExpr, bool],
    then: Union[QCallable, Callable[[], None]],
    else_: Union[QCallable, Callable[[], None], int] = _MISSING_VALUE,
) -> None:
    _validate_operand(then)
    if else_ != _MISSING_VALUE:
        _validate_operand(else_)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        ClassicalIf(
            condition=Expression(expr=str(condition)),
            then=_operand_to_body(then, "then"),
            else_=_operand_to_body(else_, "else") if else_ != _MISSING_VALUE else [],  # type: ignore[arg-type]
            source_ref=source_ref,
        )
    )


@overload  # FIXME: Remove overloading (CAD-21932)
def control(
    ctrl: Union[QBit, QArray[QBit]], stmt_block: Union[QCallable, Callable[[], None]]
) -> None:
    pass


@overload
def control(
    ctrl: SymbolicExpr, stmt_block: Union[QCallable, Callable[[], None]]
) -> None:
    pass


def control(
    ctrl: Union[SymbolicExpr, QBit, QArray[QBit]],
    stmt_block: Optional[Union[QCallable, Callable[[], None]]] = None,
    operand: Optional[Union[QCallable, Callable[[], None]]] = None,
) -> None:
    if operand is not None:
        warnings.warn(
            "Parameter 'operand' of function 'control' has been renamed to "
            "'stmt_block'. Parameter 'operand' will be deprecated in a future "
            "release.\nHint: Change `control(ctrl=..., operand=...)` to "
            "`control(ctrl=..., stmt_block=...)` or `control(..., ...)`.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        stmt_block = operand
    if TYPE_CHECKING:
        assert stmt_block is not None
    _validate_operand(stmt_block)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        Control(
            expression=Expression(expr=str(ctrl)),
            body=_operand_to_body(stmt_block, "stmt_block"),
            source_ref=source_ref,
        )
    )


def inplace_add(
    value: QNum,
    target: QNum,
) -> None:
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        InplaceBinaryOperation(
            target=target.get_handle_binding(),
            value=value.get_handle_binding(),
            operation=BinaryOperation.Addition,
            source_ref=source_ref,
        )
    )


def inplace_xor(
    value: QNum,
    target: QNum,
) -> None:
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        InplaceBinaryOperation(
            target=target.get_handle_binding(),
            value=value.get_handle_binding(),
            operation=BinaryOperation.Xor,
            source_ref=source_ref,
        )
    )


@overload  # FIXME: Remove overloading (CAD-21932)
def within_apply(
    within: Callable[[], None],
    apply: Callable[[], None],
) -> None:
    pass


@overload
def within_apply(
    within: Callable[[], List[None]],
    apply: Callable[[], List[None]],
) -> None:
    pass


def within_apply(  # type:ignore[misc]
    within: Optional[Callable[[], None]] = None,
    apply: Optional[Callable[[], None]] = None,
    compute: Optional[Callable[[], None]] = None,
    action: Optional[Callable[[], None]] = None,
) -> None:
    if compute is not None or action is not None:
        warnings.warn(
            "Parameters 'compute' and 'action' of function 'within_apply' have "
            "been renamed to 'within' and 'apply' respectively. Parameters 'compute' "
            "and 'action' will be deprecated in a future release.\nHint: Change "
            "`within_apply(compute=..., action=...)` to "
            "`within_apply(within=..., apply=...)` or `within_apply(..., ...)`.",
            category=DeprecationWarning,
            stacklevel=2,
        )
    if compute is not None:
        within = compute
    if action is not None:
        apply = action
    if TYPE_CHECKING:
        assert within is not None
        assert apply is not None
    _validate_operand(within)
    _validate_operand(apply)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        WithinApply(
            compute=_operand_to_body(within, "within"),
            action=_operand_to_body(apply, "apply"),
            source_ref=source_ref,
        )
    )


def repeat(count: Union[SymbolicExpr, int], iteration: Callable[[int], None]) -> None:
    _validate_operand(iteration)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    iteration_operand = prepare_arg(
        QuantumOperandDeclaration(
            name=REPEAT_OPERATOR_NAME,
            positional_arg_declarations=[
                ClassicalParameterDeclaration(name="index", classical_type=Integer()),
            ],
        ),
        iteration,
        repeat.__name__,
        "iteration",
    )
    if not isinstance(iteration_operand, QuantumLambdaFunction):
        raise ClassiqValueError(
            "Argument 'iteration' to 'repeat' should be a callable that takes one integer argument."
        )

    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        Repeat(
            iter_var=inspect.getfullargspec(iteration).args[0],
            count=Expression(expr=str(count)),
            body=iteration_operand.body,
            source_ref=source_ref,
        )
    )


@overload  # FIXME: Remove overloading (CAD-21932)
def power(
    exponent: SymbolicExpr,
    stmt_block: Union[QCallable, Callable[[], None]],
) -> None:
    pass


@overload
def power(
    exponent: int,
    stmt_block: Union[QCallable, Callable[[], None]],
) -> None:
    pass


def power(
    exponent: Optional[Union[SymbolicExpr, int]] = None,
    stmt_block: Optional[Union[QCallable, Callable[[], None]]] = None,
    power: Optional[Union[SymbolicExpr, int]] = None,
    operand: Optional[Union[QCallable, Callable[[], None]]] = None,
) -> None:
    if power is not None or operand is not None:
        warnings.warn(
            "Parameters 'exponent' and 'operand' of function 'power' have been "
            "renamed to 'exponent' and 'stmt_block' respectively. Parameters "
            "'exponent' and 'operand' will be deprecated in a future release.\nHint: "
            "Change `power(power=..., operand=...)` to "
            "`power(exponent=..., stmt_block=...)` or `power(..., ...)`.",
            category=DeprecationWarning,
            stacklevel=2,
        )
    if power is not None:
        exponent = power
    if operand is not None:
        stmt_block = operand
    if TYPE_CHECKING:
        assert exponent is not None
        assert stmt_block is not None
    _validate_operand(stmt_block)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        Power(
            power=Expression(expr=str(exponent)),
            body=_operand_to_body(stmt_block, "stmt_block"),
            source_ref=source_ref,
        )
    )


@overload  # FIXME: Remove overloading (CAD-21932)
def invert(stmt_block: QCallable) -> None:
    pass


@overload
def invert(stmt_block: Callable[[], None]) -> None:
    pass


def invert(
    stmt_block: Optional[Union[QCallable, Callable[[], None]]] = None,
    operand: Optional[Union[QCallable, Callable[[], None]]] = None,
) -> None:
    if operand is not None:
        warnings.warn(
            "Parameter 'operand' of function 'invert' has been renamed to "
            "'stmt_block'. Parameter 'operand' will be deprecated in a future "
            "release.\nHint: Change `invert(operand=...)` to `invert(stmt_block=...)` "
            "or `invert(...)`.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        stmt_block = operand
    if TYPE_CHECKING:
        assert stmt_block is not None
    _validate_operand(stmt_block)
    assert QCallable.CURRENT_EXPANDABLE is not None
    source_ref = get_source_ref(sys._getframe(1))
    QCallable.CURRENT_EXPANDABLE.append_statement_to_body(
        Invert(body=_operand_to_body(stmt_block, "stmt_block"), source_ref=source_ref)
    )


def _validate_operand(stmt_block: Any) -> None:
    if stmt_block is not None:
        return
    currentframe: FrameType = inspect.currentframe()  # type: ignore[assignment]
    operation_frame: FrameType = currentframe.f_back  # type: ignore[assignment]
    operation_frame_info: inspect.Traceback = inspect.getframeinfo(operation_frame)
    operation_name: str = operation_frame_info.function

    context = operation_frame_info.code_context
    assert context is not None
    operand_arg_name = context[0].split("_validate_operand(")[1].split(")")[0]

    error_message = (
        f"{operation_name!r} is missing required argument for {operand_arg_name!r}."
    )
    error_message += _get_operand_hint(
        operation_name=operation_name,
        operand_arg_name=operand_arg_name,
        params=inspect.signature(operation_frame.f_globals[operation_name]).parameters,
    )
    raise ClassiqValueError(error_message)


def _get_operand_hint_args(
    params: Mapping[str, inspect.Parameter], operand_arg_name: str, operand_value: str
) -> str:
    return ", ".join(
        [
            (
                f"{param.name}={operand_value}"
                if param.name == operand_arg_name
                else f"{param.name}=..."
            )
            for param in params.values()
            if param.name != "operand"  # FIXME: Remove compatibility (CAD-21932)
        ]
    )


def _get_operand_hint(
    operation_name: str, operand_arg_name: str, params: Mapping[str, inspect.Parameter]
) -> str:
    return (
        f"\nHint: To call a function under {operation_name!r} use a lambda function as in "
        f"'{operation_name}({_get_operand_hint_args(params, operand_arg_name, 'lambda: f(q)')})' "
        f"or pass the quantum function directly as in "
        f"'{operation_name}({_get_operand_hint_args(params, operand_arg_name, 'f')})'."
    )


def _operand_to_body(
    callable_: Union[QCallable, Callable[[], None]], param_name: str
) -> StatementBlock:
    op_name = sys._getframe(1).f_code.co_name
    if (
        isinstance(callable_, QCallable)
        and len(callable_.func_decl.positional_arg_declarations) > 0
    ):
        raise ClassiqValueError(
            f"Callable argument {callable_.func_decl.name!r} to {op_name!r} should "
            f"not accept arguments."
        )
    to_operand = prepare_arg(
        QuantumOperandDeclaration(name=""), callable_, op_name, param_name
    )
    if isinstance(to_operand, str):
        return [QuantumFunctionCall(function=to_operand)]
    elif isinstance(to_operand, QuantumLambdaFunction):
        return to_operand.body
    else:
        raise ValueError(f"Unexpected operand type: {type(to_operand)}")


__all__ = [
    "bind",
    "control",
    "invert",
    "if_",
    "inplace_add",
    "inplace_xor",
    "power",
    "within_apply",
    "repeat",
]


def __dir__() -> List[str]:
    return __all__
