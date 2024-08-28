from typing import (
    Any,
    Generic,
    Iterator,
    Optional,
    TypeVar,
    Callable,
    List as PyList,
)

from pydrew.modules.dictionary import Dictionary

T = TypeVar("T")


class List(Generic[T]):
    """
    A custom list implementation that provides additional functionality.

        list_ (Union[PyList[T] | "List[T]" | Iterator[T] | None], optional): The initial list to initialize from. Defaults to None.

    Attributes:
        _data (PyList[T]): The internal list that stores the data.

    Methods:
        concat(list_: PyList[T] | "List[T]") -> "List[T]":
        to_list() -> PyList[T]:
        add(item: T, index: Optional[int] = None) -> "List[T]":
        removeAt(index: Optional[int] = None) -> T:
        remove(element: T):
        at_index(index: int) -> T:
        first() -> T | None:
        last() -> T | None:
        where(func: Callable[[T], PyList[T]]) -> "List[T]":
        select(func: Callable[[T], Any]) -> "List[Any]":
        sort(func: Callable[[T], Any]) -> "List[T]":
        group_by(property: str) -> "List[List[T]]":
            Groups the items in the list based on a given property.
        reverse() -> "List[T]":
        clear() -> "List[T]":
        count() -> int:

    Magic Methods:
        __getitem__(index):
            Allows access with `obj[index]`.
        __setitem__(index, value):
            Allows setting item with `obj[index] = value`.
        __iter__():
            Returns an iterator for the list.
        __len__():
            Returns the length of the list.
        __delitem__(index):
            Removes and returns the item at the specified index.
        __repr__() -> str:
            Returns a string representation of the list.
        __str__() -> str:
            Returns a string representation of the list.
        __eq__(other: Any) -> bool:
            Checks if the list is equal to another list or PyList.
        __ne__(other: object) -> bool:
            Checks if the list is not equal to another list or PyList.
        __hash__() -> int:
            Returns the hash value of the list.
        __bool__() -> bool:
            Checks if the list is empty.
    """

    def __init__(self, list_: PyList[T] | "List[T]" | Iterator[T] | None = None):
        self._data: PyList[T]
        if list_ is None:
            self._data = []  # Initialize to a new empty list
        elif isinstance(list_, List):
            # Initialize with items from another List instance
            self._data = list_._data.copy()
        elif isinstance(list_, Iterator):
            # Initialize with items from an iterator
            self._data = list(list_)
        else:
            # Initialize with a copy of the provided list
            self._data = list_.copy()

    def concat(self, list_: PyList[T] | "List[T]") -> "List[T]":
        """
        Concatenates the given list with the current list and returns a new list.

        Parameters:
        - list_ (PyList[T] | 'List[T]'): The list to be concatenated with the current list.

        Returns:
        - List[T]: The new list obtained by concatenating the current list with the given list.
        """
        if isinstance(list_, List):
            self._data += list_._data
        else:
            self._data += list_
        return self

    def extend(self, list_: PyList[T] | "List[T]") -> "List[T]":
        """
        Extends the current list with the given list.

        Parameters:
            list_ (PyList[T] | 'List[T]'): The list to extend the current list with.

        Returns:
            List[T]: The current list extended with the given list.
        """
        if isinstance(list_, List):
            self._data.extend(list_._data)
        else:
            self._data.extend(list_)
        return self

    def to_list(self) -> PyList[T]:
        """
        Returns the internal list representation of the object.

        Returns:
            PyList[T]: The internal list representation of the object.
        """
        return self._data

    def add(self, item: T, index: Optional[int] = None) -> "List[T]":
        """
        Adds an item to the list.

        Parameters:
            item (T): The item to be added to the list.

        Returns:
            List[T]: The list with the added item.
        """
        if index is None:
            self._data.append(item)
        else:
            self._data.insert(index, item)
        return self

    def remove_at(self, index: Optional[int] = None) -> T:
        """
        Removes and returns the last item from the list if no index is passed,
        otherwise removes and returns the item at the specified index.

        Parameters:
            index (int, optional): The index of the item to be removed. Defaults to None and remove the last item.

        Returns:
            T: The removed item.
        """
        if index is None:
            return self._data.pop()
        else:
            return self._data.pop(index)

    def remove(self, element: T):
        """
        Removes the first occurrence of the specified element from the list.

        Parameters:
            element (T): The element to be removed from the list.
        """
        self._data.remove(element)
        return self

    def at_index(self, index: int) -> T:
        """
        Returns the item at the specified index.

        Parameters:
            index (int): The index of the item to be returned.

        Returns:
            T: The item at the specified index.
        """
        return self._data[index]

    def first(self) -> T | None:
        """
        Returns the first item in the list.

        Returns:
            T | None: The first item in the list, or None if the list is empty.
        """
        return self._data[0] if self.count() > 0 else None

    def last(self) -> T | None:
        """
        Returns the last item in the list.

        Returns:
            T | None: The last item in the list, or None if the list is empty.
        """
        return self._data[-1] if self.count() > 0 else None

    def where(self, func: Callable[[T], bool]) -> "List[T]":
        """
        Filters the list based on a given condition.

        Parameters:
            func: The condition to filter the list.

        Returns:
            List[T]: The filtered list.
        """
        return List(list(filter(func, self._data)))

    def select(self, func: Callable[[T], Any]) -> "List[Any]":
        """
        Returns a new list with each item transformed using the given function.

        Parameters:
            func: The function to transform each item in the list.

        Returns:
            List[Any]: The new list with transformed items.
        """
        return List(list(map(func, self._data)))

    def sort(self, func: Callable[[T], Any], reverse: bool = False) -> "List[T]":
        """
        Sorts the list based on a given comparison function.

        Parameters:
            func: The comparison function to sort the list.

        Returns:
            List[T]: The sorted list.
        """
        sorted_list = sorted(self._data, key=func, reverse=reverse)
        return List(sorted_list)

    def group_by(
            self, property: str, as_list: bool = True
    ) -> Dictionary[Any, "List[T]"]:
        """
        Groups the items in the list based on a given function.

        Parameters:
            func: The function to group the items in the list.

        Returns:
            List[T]: The grouped list.

        Raises:
            ValueError: If the property is not found in the items.
        """
        grouped: Dictionary[Any, List[T]] = Dictionary()
        for item in self._data:
            # Check if the item is a dictionary or an object
            key: Any
            if isinstance(item, dict):
                key = item.get(property)  # Dictionary access
            else:
                key = getattr(item, property)  # Object property access
            if key is None:
                raise KeyError(
                    f"Property '{property}' not found in the items.")
            if key not in grouped.keys():
                grouped[key] = List()
            grouped[key].add(item)
        return grouped

    def group_by_func(
            self, func: Callable[[T], Any], as_list: bool = True
    ) -> Dictionary[Any, "List[T]"]:
        """
        Groups the items in the list based on a given function.

        Parameters:
            func: The function to group the items in the list.

        Returns:
            List[T]: The grouped list.

        Raises:
            ValueError: If the property is not found in the items.
        """
        grouped: Dictionary[Any, List[T]] = Dictionary()
        for item in self._data:
            key = func(item)
            if key is None:
                raise ValueError(
                    f"Property '{property}' not found in the items.")
            if key not in grouped.keys():
                grouped[key] = List()
            grouped[key].add(item)
        return grouped

    def to_dict(self):
        """
        Converts the list to a dictionary.

        Returns:
            Dictionary: The dictionary representation of the list.
        """
        data = {}
        for index, item in enumerate(self._data):
            data[index] = item
        return data

    def reverse(self) -> "List[T]":
        """
        Reverses the order of items in the list.

        Returns:
            List[T]: The reversed list.
        """
        self._data.reverse()
        return self

    def clear(self) -> "List[T]":
        """
        Removes all items from the list.

        Returns:
            List[T]: The cleared list.
        """
        self._data.clear()
        return self

    def count(self) -> int:
        """
        Returns the number of items in the list.

        Returns:
            int: The number of items in the list.
        """
        return len(self._data)

    def copy(self) -> "List[T]":
        """
        Returns a shallow copy of the list.

        Returns:
            List[T]: A shallow copy of the list.
        """
        return List(self._data)

    # Magic methods

    def __add__(self, other: "List[T]") -> "List[T]":
        return self.concat(other)

    def __sub__(self, other: "List[T]") -> "List[T]":
        return self.where(lambda x: x not in other)

    def __getitem__(self, index):
        return self._data[index]  # Allows access with `obj[index]`

    def __setitem__(self, index, value):
        # Allows setting item with `obj[index] = value`
        self._data[index] = value

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __delitem__(self, index):
        self.remove_at(index)

    def __repr__(self) -> str:
        result: str = ""
        for item in self._data:
            result += str(item) + ","
        return result

    def __str__(self) -> str:
        result: str = ""
        for item in self._data:
            result += str(item) + "\n"
        return result

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, List):
            return self._data == other._data
        if isinstance(other, PyList):
            return self._data == other
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def __hash__(self) -> int:
        return super().__hash__()

    def __bool__(self) -> bool:
        return self.count() > 0
