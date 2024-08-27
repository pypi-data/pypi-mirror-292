import time
from collections import OrderedDict
from typing import Any

from .cache_strategy import CacheStrategy


class SlidingWindowEvictionPolicy(CacheStrategy):
    def __init__(self, expiration_seconds: float):
        self.expiration_seconds = expiration_seconds  # Sliding window duration in seconds
        self.timestamps: OrderedDict[Any, float] = OrderedDict()

    def _is_expired(self, key: Any) -> bool:
        """Check if the item is expired based on its timestamp."""
        return (time.time() - self.timestamps[key]) > self.expiration_seconds

    def on_access(self, cache: "Cache", key: Any) -> None:
        """Refresh the item's timestamp to keep it in the sliding window."""
        if self._is_expired(key):
            cache.cache.pop(key, None)
            self.timestamps.pop(key, None)
            return None
        self.timestamps[key] = time.time()
        cache.cache.move_to_end(key=key)
        # return cache.cache.get(key)

    def on_insert(self, cache: "Cache", key: Any) -> None:
        """Insert an item, evicting if necessary based on sliding window."""
        self.timestamps[key] = time.time()
        self.evict(cache=cache)
        # if len(cache.cache) >= cache.capacity:
        #     cache.cache.popitem(last=False)

    def evict(self, cache: "Cache") -> None:
        """Evict items that fall outside the sliding window."""
        current_time = time.time()
        keys_to_evict = [key for key, timestamp in self.timestamps.items()
                         if (current_time - timestamp) > self.expiration_seconds]
        for key in keys_to_evict:
            cache.cache.pop(key, None)
            self.timestamps.pop(key, None)

        if len(cache.cache) >= cache.capacity:
            cache.cache.popitem(last=False)
