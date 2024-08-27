from typing import Any

from .cache_strategy import CacheStrategy


class LRUEvictionPolicy(CacheStrategy):
    def on_access(self, cache: "Cache", key: Any) -> Any:
        """Move the accessed item to the end to mark it as most recently used."""
        cache.cache.move_to_end(key=key)

    def on_insert(self, cache: "Cache", key: Any) -> None:
        """ Before item is inserted; check if we need to evict Least Recently Used item """
        if len(cache.cache) >= cache.capacity:
            self.evict(cache=cache)

    def evict(self, cache: "Cache") -> None:
        """Evict the least recently used item."""
        if cache.cache:
            cache.cache.popitem(last=False)
