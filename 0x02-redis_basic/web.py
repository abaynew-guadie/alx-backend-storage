#!/usr/bin/env python3
"""web module
"""
from functools import wraps
from typing import Callable
import redis
import requests

_redis = redis.Redis()
_redis.flushdb()


def count_requests(method: Callable) -> Callable:
    """count_requests function

    Args:
        method (Callable): method

    Returns:
        Callable: wrapper
    """
    @wraps(method)
    def wrapper(*args, **kwargs):
        """wrapper function

        Returns:
            [type]: wrapper
        """
        url = args[0]
        cached = _redis.get(f"cached:{url}")
        if cached:
            return cached.decode("utf-8")
        response = method(*args, **kwargs)
        _redis.incr(f"count:{url}")
        _redis.setex(f"cached:{url}", 10, response)
        return response
    return wrapper


@count_requests
def get_page(url: str) -> str:
    """get_page function

    Args:
        url (str): url

    Returns:
        str: response
    """
    response = requests.get(url, timeout=10)
    return response.text
