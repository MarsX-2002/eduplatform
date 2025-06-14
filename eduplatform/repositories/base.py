from abc import ABC, abstractmethod
from typing import Dict, List, Optional, TypeVar, Generic, Type, Any

T = TypeVar('T')

class BaseRepository(Generic[T], ABC):
    """Base repository class for handling CRUD operations on models."""
    
    def __init__(self):
        self._storage: Dict[str, T] = {}
    
    @abstractmethod
    def _get_key(self, item: T) -> str:
        """Get the unique key for an item."""
        pass
    
    def add(self, item: T) -> T:
        """Add a new item to the repository."""
        key = self._get_key(item)
        if key in self._storage:
            raise ValueError(f"Item with key '{key}' already exists")
        self._storage[key] = item
        return item
    
    def get(self, key: str) -> Optional[T]:
        """Get an item by its key."""
        return self._storage.get(key)
    
    def get_all(self) -> List[T]:
        """Get all items in the repository."""
        return list(self._storage.values())
    
    def update(self, item: T) -> bool:
        """Update an existing item."""
        key = self._get_key(item)
        if key not in self._storage:
            return False
        self._storage[key] = item
        return True
    
    def delete(self, key: str) -> bool:
        """Delete an item by its key."""
        if key in self._storage:
            del self._storage[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if an item with the given key exists."""
        return key in self._storage
    
    def count(self) -> int:
        """Get the number of items in the repository."""
        return len(self._storage)
    
    def clear(self) -> None:
        """Remove all items from the repository."""
        self._storage.clear()
    
    def find(self, predicate) -> List[T]:
        """Find items that match the given predicate function."""
        return [item for item in self._storage.values() if predicate(item)]
    
    def find_one(self, predicate) -> Optional[T]:
        """Find the first item that matches the given predicate function."""
        return next((item for item in self._storage.values() if predicate(item)), None)
