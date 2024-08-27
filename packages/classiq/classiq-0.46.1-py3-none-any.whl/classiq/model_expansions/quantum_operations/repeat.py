from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.builtins.internal_operators import (
    REPEAT_OPERATOR_NAME,
)
from classiq.interface.generator.functions.classical_type import Integer
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.repeat import Repeat

from classiq.model_expansions.closure import FunctionClosure
from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import Scope


class RepeatEmitter(Emitter[Repeat]):
    def emit(self, repeat: Repeat, /) -> None:
        count = self._interpreter.evaluate(repeat.count).as_type(int)
        for i in range(count):
            with self._propagated_var_stack.capture_variables(repeat):
                iteration_function = FunctionClosure.create(
                    name=REPEAT_OPERATOR_NAME,
                    positional_arg_declarations=[
                        ClassicalParameterDeclaration(
                            name=repeat.iter_var, classical_type=Integer()
                        )
                    ],
                    body=repeat.body,
                    scope=Scope(parent=self._current_scope),
                )
                self._emit_quantum_function_call(
                    iteration_function, [Expression(expr=str(i))]
                )
