import time
from collections import OrderedDict
from typing import Any, Dict, DefaultDict, List
from _collections import defaultdict

from .cache_strategy import CacheStrategy


class LFUEvictionPolicy(CacheStrategy):
    def __init__(self):
        self.frequency_dict: DefaultDict[Any, float] = defaultdict(int)
        self.timestamps: OrderedDict[Any, float] = OrderedDict()

    # def _is_expired(self, key: Any) -> bool:
    #     """Check if the item is expired based on its timestamp."""
    #     return (time.time() - self.key_access_count_dict[key]) > self.ttl

    def on_access(self, cache: "Cache", key: Any) -> None:
        """ Move key to the end and update frequency dict if item is accessed """
        self.frequency_dict[key] += 1
        cache.cache.move_to_end(key=key)

    def on_insert(self, cache: "Cache", key: Any) -> None:
        """Insert an item into the cache, evicting if necessary."""
        if len(cache.cache) >= cache.capacity:
            self.evict(cache=cache)
            # cache.cache.popitem(last=False)
        self.timestamps[key] = time.time()
        self.frequency_dict[key] = 0

    def evict(self, cache: "Cache") -> None:
        """Evict items based on expiration and capacity."""

        # Initialize variables to track the least frequent and oldest key
        least_frequency = float('inf')
        oldest_timestamp = float('inf')
        selected_key = None

        for key in self.frequency_dict:
            frequency = self.frequency_dict[key]
            timestamp = self.timestamps[key]

            # Compare based on frequency first, then timestamp if necessary
            if frequency < least_frequency or (frequency == least_frequency and timestamp < oldest_timestamp):
                least_frequency = frequency
                oldest_timestamp = timestamp
                selected_key = key
        cache.cache.pop(selected_key)

        # If the cache is still at capacity: remove the least recently used
        if len(cache.cache) >= cache.capacity:
            cache.cache.popitem(last=False)
