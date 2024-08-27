import random
from typing import Any

from .cache_strategy import CacheStrategy


class RandomEvictionPolicy(CacheStrategy):
    def on_access(self, cache: "Cache", key: Any) -> Any:
        """ Do Nothing """
        pass

    def on_insert(self, cache: "Cache", key: Any) -> None:
        """ Before item is inserted; check if we need to evict one """
        if len(cache.cache) >= cache.capacity:
            self.evict(cache=cache)

    def evict(self, cache: "Cache") -> None:
        """Evict the least recently used item."""
        if cache.cache:
            random_key = random.choice(list(cache.cache.keys()))
            cache.cache.pop(random_key)
