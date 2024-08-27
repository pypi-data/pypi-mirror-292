from typing import List

from classiq.interface.model.classical_if import ClassicalIf
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.statement_block import ConcreteQuantumStatement

from classiq.model_expansions.closure import FunctionClosure
from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import Scope


def _is_all_identity_calls(body: List[ConcreteQuantumStatement]) -> bool:
    return all(
        isinstance(stmt, QuantumFunctionCall) and stmt.func_name.lower() == "identity"
        for stmt in body
    )


class ClassicalIfEmitter(Emitter[ClassicalIf]):
    def emit(self, classical_if: ClassicalIf, /) -> None:
        condition = self._interpreter.evaluate(classical_if.condition).as_type(bool)
        body: List[ConcreteQuantumStatement] = (
            classical_if.then if condition else classical_if.else_
        )
        if _is_all_identity_calls(body):
            return

        if not self._should_wrap(body):
            for stmt in body:
                self._interpreter.emit_statement(stmt)
            return

        then_else_func = FunctionClosure.create(
            name="then" if condition else "else",
            body=body,
            scope=Scope(parent=self._current_scope),
        )
        with self._propagated_var_stack.capture_variables(classical_if):
            self._emit_quantum_function_call(then_else_func, list())
