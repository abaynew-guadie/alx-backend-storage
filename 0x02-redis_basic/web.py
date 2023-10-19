#!/usr/bin/env python3
"""use requests module to obtain the HTML content of a particular URL and returns it"""

import redis
import requests
from typing import Callable
from functools import wraps


def access(method: Callable) -> Callable:
    """decorator for get_page"""
    @wraps(method)
    def count(url: str) -> str:
        """track how many times a particular URL was accessed"""
        redis_client = redis.Redis()
        redis_client.incr(f'count:{url}')
        cached = redis_client.get(f'cached:{url}')
        if cached:
            return cached.decode('utf-8')
        res = method(url)
        redis_client.setex(f'cached:{url}', 10, res)
        return res
    return count


@access
def get_page(url: str) -> str:
    """send request to url"""
    return requests.get(url).text


if __name__ == '__main__':
    get_page('http://slowwly.robertomurray.co.uk')
