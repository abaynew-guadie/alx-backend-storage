#!/usr/bin/env python3
"""exercise module
"""
import redis
from uuid import uuid4
from typing import Callable, Optional, Union
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """count_calls function

    Args:
        method[Callable]:

    returns:
        Callable:
    """
    key = method.__qualname__

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper decorated function

        Returns:
        """
        self._redis.incr(key)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """call_history function

    Args:
        method[Callable]:

    Returns:
        Callable:
    """
    key = method.__qualname__
    inputs, outputs = key + ":inputs", key + ":outputs"

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """wrapper decorated function

        Returns:
        """
        self._redis.rpush(inputs, str(args))
        output = str(method(self, *args, **kwargs))
        self._redis.rpush(outputs, output)
        return output

    return wrapper


def replay(method: Callable) -> None:
    """replay function

    Args:
        method[Callable]:
    """
    key = method.__qualname__
    inputs, outputs = key + ":inputs", key + ":outputs"
    redis = method.__self__._redis
    count = redis.get(key).decode("utf-8")
    print(f"{key} was called {count} times:")
    IOTuple = zip(redis.lrange(inputs, 0, -1), redis.lrange(outputs, 0, -1))
    for inp, outp in list(IOTuple):
        attr, data = inp.decode("utf-8"), outp.decode("utf-8")
        print(f"{key}(*{attr}) -> {data}")


class Cache:
    """Cache class"""

    def __init__(self):
        """init function"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """store function

        Args:
            data[str, bytes, int, float]: value

        Returns:
            str: key
        """
        key = str(uuid4())
        self._redis.set(key, data)
        return str(key)

    def get(
        self, key: str, fn: Optional[Callable] = None
    ) -> Union[str, bytes, int, float]:
        """get function"""
        value = self._redis.get(key)
        if fn:
            value = fn(value)
        return value

    def get_str(self, data: str) -> str:
        """get_str function

        Args:
            key[str]:

        Returns:
            str:
        """
        return data.decode("utf-8")

    def get_int(self, data: str) -> int:
        """get_int function

        Args:
            key[str]:

        Returns:
            int:
        """
        return int(data)
