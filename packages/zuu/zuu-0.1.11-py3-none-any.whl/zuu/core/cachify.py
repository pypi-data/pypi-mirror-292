import functools
from typing import Any, Callable, Dict, Optional, Tuple


def cachify(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to cache the result of a function.
    """
    cache: Dict[Tuple[Any, ...], Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (*args, *kwargs.items())
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]

    return wrapper


def timed_cachify(
    expiration: float,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to cache the result of a function with an expiration time.

    :param expiration: Time in seconds for which the cached result is valid.
    """
    import time

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache: Dict[Tuple[Any, ...], Tuple[Any, float]] = {}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = (*args, *kwargs.items())
            current_time = time.time()

            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < expiration:
                    return result

            result = func(*args, **kwargs)
            cache[key] = (result, current_time)
            return result

        return wrapper

    return decorator


def lru_cachify(
    maxsize: Optional[int] = 128,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator to cache the result of a function using LRU (Least Recently Used) strategy.

    :param maxsize: Maximum number of items to store in the cache. If None, the cache can grow without bound.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.lru_cache(maxsize=maxsize)
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapper

    return decorator
