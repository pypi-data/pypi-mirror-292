from typing import Any

from .cache_strategy import CacheStrategy


class DefaultEvictionPolicy(CacheStrategy):
    def on_access(self, cache: "Cache", key: Any) -> None:
        """ Method that is called before a key is accessed in the cache."""
        # Does nothing; key order is maintained
        pass

    def on_insert(self, cache: "Cache", key: Any) -> None:
        """Method that is called before a new key-value pair is inserted into the cache."""
        if len(cache.cache) >= cache.capacity:
            self.evict(cache=cache)

    def evict(self, cache: "Cache") -> None:
        """ Remove the oldes ."""
        cache.cache.popitem(last=False)
