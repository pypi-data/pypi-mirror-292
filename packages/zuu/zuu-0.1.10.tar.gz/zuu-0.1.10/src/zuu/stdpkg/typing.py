from typing import get_overloads
import inspect
import typing


def get_overload_signatures(func):
    """
    A function that yields the signature of each overload function in the given function.
    """
    overloads = get_overloads(func)
    for overloadFunc in overloads:
        yield inspect.signature(overloadFunc)


def bind_overload(overloadFunc, *args, **kwargs):
    """
    A function that binds the overload function with the given arguments and keyword arguments.
    """
    for sig in get_overload_signatures(overloadFunc):
        try:
            return sig.bind(*args, **kwargs).arguments
        except TypeError:
            pass


def is_typedict(obj: dict, *choices):
    """
    A function that checks if the given object is a TypedDict and if it is, if it is of the given type.
    """
    if not isinstance(obj, dict):
        return
    if not all(isinstance(o, type) and hasattr(o, "__annotations__") for o in choices):
        return

    for choice in choices:

        try:
            if not (
                (
                    all(k in choice.__annotations__ for k in obj)
                    or getattr(choice, "__total__", True) is False
                )
                and all(
                    isinstance(obj[k], choice.__annotations__[k])
                    for k in choice.__annotations__
                )
            ):
                continue

            choice(**obj)
            return choice
        except:  # noqa
            pass
