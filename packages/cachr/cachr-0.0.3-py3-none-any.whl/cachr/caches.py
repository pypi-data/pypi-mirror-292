from collections import OrderedDict
from typing import Any, Optional, Callable

from . import policies


class Cache:
    cache: OrderedDict
    capacity: int

    def __init__(self, capacity: int, cache_strategy: policies.CacheStrategy = policies.DefaultEvictionPolicy()):
        self.cache: OrderedDict[Any, Any] = OrderedDict()
        self.capacity: int = capacity
        self._cache_strategy = cache_strategy

    def get(self, key: Any) -> Optional[Any]:
        """Retrieve value from cache by provided key - cache hit or miss."""

        if key not in self.cache:
            return None
        self._cache_strategy.on_access(self, key)
        return self.cache.get(key)

    def put(self, key: Any, value: Any) -> None:
        """Insert a key-value pair into the cache."""
        if key in self.cache:
            self._cache_strategy.on_access(self, key)
        else:
            self._cache_strategy.on_insert(self, key)
        self.cache[key] = value

    # region CONVENIENCE METHODS
    def clear(self):
        self.cache.clear()

    def size(self) -> int:
        """ Return the number of items in the cache """
        return len(self.cache)
    # endregion

    # region DECORATOR
    def __call__(self, func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # The ars and kwargs will be the key of the cache
            key = args + tuple(kwargs.items())

            # Try to retrieve result from cache
            result = self.get(key)

            # If key not in cache: retrieve and return
            if result is None:
                result = func(*args, **kwargs)
                self.put(key=key, value=result)
            return result

        return wrapper
    # endregion




class LRUCache(Cache):
    def __init__(self, capacity: int):
        super().__init__(capacity=capacity, cache_strategy=policies.LRUEvictionPolicy())


class TTLCache(Cache):
    def __init__(self, capacity: int, ttl_seconds:float):
        super().__init__(capacity=capacity, cache_strategy=policies.TTLEvictionPolicy(ttl_seconds=ttl_seconds))


class SlidingWindowCache(Cache):
    def __init__(self, capacity: int, expiration_seconds:float):
        super().__init__(capacity=capacity, cache_strategy=policies.SlidingWindowEvictionPolicy(expiration_seconds=expiration_seconds))

class LFUCache(Cache):
    def __init__(self, capacity: int, ):
        super().__init__(capacity=capacity, cache_strategy=policies.LFUEvictionPolicy())

class RandomReplaceCache(Cache):
    def __init__(self, capacity: int, ):
        super().__init__(capacity=capacity, cache_strategy=policies.RandomEvictionPolicy())
