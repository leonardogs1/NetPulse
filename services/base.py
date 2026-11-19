from abc import ABC, abstractmethod

import psutil


class BaseMonitoring(ABC):
    """Contract every monitor (network, processes, disk, ...) follows.

    Subclasses must implement collect_all() and collect_by_id().
    The other methods have sensible defaults that can be overridden.
    """

    def __init__(self):
        # Kept as an attribute so tests can swap in a fake.
        self.system = psutil

    @abstractmethod
    def collect_all(self):
        """Return a fresh snapshot of every item this monitor tracks."""

    @abstractmethod
    def collect_by_id(self, item_id):
        """Return the item with this id, or None if it doesn't exist."""

    def stop_by_id(self, item_id):
        """Stop an item (e.g. end a process). Not every monitor supports it."""
        raise NotImplementedError(f"{type(self).__name__} does not support stopping items")

    def print_all(self):
        for item in self.collect_all():
            print(item)

    def print_by_id(self, item_id):
        item = self.collect_by_id(item_id)
        print(item if item is not None else f"Nothing found with id {item_id!r}")
