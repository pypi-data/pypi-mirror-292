from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator, Optional

from classiq.interface.exceptions import ClassiqError

if TYPE_CHECKING:
    from classiq.model_expansions.interpreter import Interpreter

_GENERATIVE_ENABLED_SWITCH: bool = True
_GENERATIVE_MODE: bool = False
_FRONTEND_INTERPRETER: Optional["Interpreter"] = None


def is_generative_mode() -> bool:
    return _GENERATIVE_MODE


@contextmanager
def generative_mode_context(generative: bool) -> Iterator[None]:
    global _GENERATIVE_MODE
    previous = _GENERATIVE_MODE
    _GENERATIVE_MODE = generative
    yield
    _GENERATIVE_MODE = previous


@contextmanager
def enable_generative_expansion(enabled: bool) -> Iterator[None]:
    global _GENERATIVE_ENABLED_SWITCH
    previous = _GENERATIVE_ENABLED_SWITCH
    _GENERATIVE_ENABLED_SWITCH = enabled
    yield
    _GENERATIVE_ENABLED_SWITCH = previous


def is_generative_expansion_enabled() -> bool:
    return _GENERATIVE_ENABLED_SWITCH


def set_frontend_interpreter(interpreter: "Interpreter") -> None:
    global _FRONTEND_INTERPRETER
    _FRONTEND_INTERPRETER = interpreter


def get_frontend_interpreter() -> "Interpreter":
    if _FRONTEND_INTERPRETER is None:
        raise ClassiqError("Interpreter was not set")
    return _FRONTEND_INTERPRETER
