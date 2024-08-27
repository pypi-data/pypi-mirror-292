import time
from collections import OrderedDict
from typing import Any

from .cache_strategy import CacheStrategy


class TTLEvictionPolicy(CacheStrategy):
    def __init__(self, ttl_seconds: float):
        self.ttl = ttl_seconds  # Time-to-live in seconds
        self.timestamps: OrderedDict[Any, float] = OrderedDict()

    def _is_expired(self, key: Any) -> bool:
        """Check if the item is expired based on its timestamp."""
        return (time.time() - self.timestamps[key]) > self.ttl

    def on_access(self, cache: "Cache", key: Any) -> None:
        """Remove the item if it's expired, otherwise update its access time."""
        if self._is_expired(key):
            cache.cache.pop(key, None)
            self.timestamps.pop(key, None)
            return None
        cache.cache.move_to_end(key=key)


    def on_insert(self, cache: "Cache", key: Any) -> None:
        """Insert an item into the cache, evicting if necessary."""
        if len(cache.cache) >= cache.capacity:
            self.evict(cache=cache)
            # cache.cache.popitem(last=False)
        self.timestamps[key] = time.time()

    def evict(self, cache: "Cache") -> None:
        """Evict items based on expiration and capacity."""

        # First remove all expired keys
        expired_keys = [key for key in self.timestamps if self._is_expired(key=key)]
        for key in expired_keys:
            cache.cache.pop(key, None)
            self.timestamps.pop(key, None)

        # If the cache is still at capacity: remove the least recently used
        if len(cache.cache) >= cache.capacity:
            cache.cache.popitem(last=False)
