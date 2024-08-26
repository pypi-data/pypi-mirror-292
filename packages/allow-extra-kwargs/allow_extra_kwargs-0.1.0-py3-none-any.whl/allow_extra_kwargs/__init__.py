import inspect
from functools import wraps

from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def allow_extra_kwargs(func: Callable[P, R]) -> Callable[P, R]:
    func_signature = inspect.signature(func)

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: Any) -> R:
        bound = func_signature.bind(*args, **kwargs)
        return func(*bound.args, **bound.kwargs)

    return wrapper
