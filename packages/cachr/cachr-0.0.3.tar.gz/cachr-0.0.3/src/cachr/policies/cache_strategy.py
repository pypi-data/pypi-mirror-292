from abc import ABC, abstractmethod
from typing import Any


class CacheStrategy(ABC):
    @abstractmethod
    def on_access(self, cache: "Cache", key: Any) -> None:
        """ Method that is called before a key is accessed in the cache."""
        pass

    @abstractmethod
    def on_insert(self, cache: "Cache", key: Any) -> None:
        """Method that is called before a new key-value pair is inserted into the cache."""
        pass

    @abstractmethod
    def evict(self, cache: "Cache") -> None:
        """Method that evicts an item based. """
        pass
