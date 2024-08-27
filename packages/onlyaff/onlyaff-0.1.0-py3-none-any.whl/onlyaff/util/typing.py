from collections.abc import Callable
from functools import update_wrapper


# Inherit the signature of one function from another. Must be adopted PEP 695.
# Ref: https://stackoverflow.com/a/77301152
def inherit_signature_from[T, **P](
    original: Callable[P, T],
) -> Callable[[Callable], Callable[P, T]]:
    """Set the signature of one function to the signature of another."""

    def wrapper(f: Callable) -> Callable[P, T]:
        return update_wrapper(f, original)  # type: ignore

    return wrapper
