#!/usr/bin/env python3

from functools import wraps
import redis
from requests import get
from typing import Callable


redis_client = redis.Redis()


def responsed_cached_or_not(fn: Callable) -> Callable:
    """
    A simple decorator to cache a http request in redis
    """
    @wraps(fn)
    def wrapper(url):
        """
        The wrapper function which gets returned
        by the decorator
        """
        redis_client.incr(f"count:{url}")
        cached_response = redis_client.get(f"cached:{url}")
        if cached_response:
            return cached_response.decode('utf-8')
        result = fn(url)
        redis_client.setex(f"cached:{url}", 10, result)
        return result

    return wrapper


@responsed_cached_or_not
def get_page(url: str) -> str:
    """
    A simple function to make http requests
    to a certain endpoint
    """
    return get(url).text
