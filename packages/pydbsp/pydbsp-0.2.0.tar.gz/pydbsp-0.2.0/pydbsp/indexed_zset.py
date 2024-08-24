from typing import Dict, Iterable, MutableSequence, Tuple, TypeVar

from zset import ZSet

T = TypeVar("T")


class IndexSet(MutableSequence[T]):
    def __init__(self, iterable=None, key=None):
        """Initialize sorted list instance.

        Optional `iterable` argument provides an initial iterable of values to
        initialize the sorted list.

        Runtime complexity: `O(n*log(n))`

        >>> sl = SortedList()
        >>> sl
        SortedList([])
        >>> sl = SortedList([3, 1, 2, 5, 4])
        >>> sl
        SortedList([1, 2, 3, 4, 5])

        :param iterable: initial values (optional)

        """
        assert key is None
        self._len = 0
        self._load = 1024
        self._lists = []
        self._maxes = []
        self._index = []
        self._offset = 0


class IndexedZSet(ZSet[T]):
    inner: Dict[T, int]

    def __init__(self, values: Dict[T, int]) -> None:
        self.inner = values

    def items(self) -> Iterable[Tuple[T, int]]:
        return self.inner.items()

    def __repr__(self) -> str:
        return self.inner.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, IndexedZSet):
            return False

        return self.inner == other.inner  # type: ignore

    def __contains__(self, item: T) -> bool:
        return self.inner.__contains__(item)

    def __getitem__(self, item: T) -> int:
        if item not in self:
            return 0

        return self.inner[item]

    def __setitem__(self, key: T, value: int) -> None:
        self.inner[key] = value
