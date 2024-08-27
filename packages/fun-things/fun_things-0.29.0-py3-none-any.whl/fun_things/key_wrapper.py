from dataclasses import dataclass
from typing import Callable, Generic, List, Optional, TypeVar

TItem = TypeVar("TItem")
TComparator = TypeVar("TComparator")
TValue = TypeVar("TValue")


@dataclass(frozen=True)
class KeyWrapper(Generic[TItem, TComparator, TValue]):
    """
    Wrapper made for `bisect`.
    """

    items: List[TItem]
    key_selector: Optional[Callable[[TItem], TComparator]] = None
    value_selector: Optional[Callable[[TItem], TValue]] = None

    def __getitem__(self, index):
        item = self.items[index]

        if self.key_selector == None:
            return item

        return self.key_selector(item)

    def __len__(self):
        return len(self.items)

    def insert(self, index, item):
        if self.value_selector != None:
            item = self.value_selector(item)

        self.items.insert(index, item)  # type: ignore
