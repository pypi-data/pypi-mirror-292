# Copyright (c) 2024 Khiat Mohammed Abderrezzak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Khiat Mohammed Abderrezzak <khiat.dev@gmail.com>


"""Sophisticate Hash Table"""


from linkedit import (
    tabulate,
    singlyLinkedList,
    _singlyLinkedListNode,
    _red,
    _green,
    _blue,
    _white,
    _cyan,
)
from typing import (
    List,
    NoReturn,
    Any,
    Tuple,
    Iterable,
    Iterator,
    Self,
)


__all__: List = [
    "hashMap",
]


_sentinel: object = object()


class hashMap:
    def __init__(self: "hashMap", data: List = None, *, detail: bool = False) -> None:
        self._hashTable: List = [None] * 26
        self.len: int = 0
        self._keys: List = []
        self._values: List = []
        self._items: List = []
        self.detail: bool = detail
        self.__hash_table(data)

    def __hash_function(
        self: "hashMap", i: int | float | complex | str | Tuple | None
    ) -> int | None | NoReturn:
        if isinstance(i, str):
            ascii_sum: int = 0
            for k in bytearray(i, "utf-8"):
                ascii_sum += k
        elif isinstance(i, int):
            ascii_sum: int = i
        elif isinstance(i, float):
            ascii_sum: int = int(i)
        elif isinstance(i, complex):
            ascii_sum: int = int((i.real % 26) + (i.imag % 26))
        elif isinstance(i, tuple):
            ascii_sum: int = 0
            for j in i:
                ascii_sum += self.__hash_function(j) % 26
        elif i is None:
            ascii_sum: int = 0
        return ascii_sum

    def __hash_table(self: "hashMap", data: List) -> None | NoReturn:
        if data is None:
            return
        try:
            for i, j in data:
                ascii_sum: int = self.__hash_function(i) % 26
                if self._hashTable[ascii_sum] is None:
                    self._hashTable[ascii_sum] = _singlyLinkedListNode((i, j))
                    self.len += 1
                    self._keys.append(i)
                    self._values.append(j)
                    self._items.append((i, j))
                else:
                    head: _singlyLinkedListNode = self._hashTable[ascii_sum]
                    while head:
                        if i is not head.data[0]:
                            helper: _singlyLinkedListNode = head
                            head: _singlyLinkedListNode | None = head.next
                        else:
                            index: int = self._keys.index(i)
                            head.data = (i, j)
                            self._values[index] = j
                            self._items[index] = (i, j)
                            break
                    else:
                        helper.next = _singlyLinkedListNode((i, j))
                        self.len += 1
                        self._keys.append(i)
                        self._values.append(j)
                        self._items.append((i, j))
        except TypeError as e0:
            raise TypeError("Invalid data type.") from None
        except ValueError as e1:
            raise ValueError("Invalid format.") from None
        except UnboundLocalError as e2:
            raise TypeError("Invalid data type.") from None

    @property
    def hashTable(self: "hashMap") -> List:
        return self._hashTable

    @hashTable.setter
    def hashTable(self: "hashMap", data: List) -> NoReturn:
        raise ValueError("read-only.")

    @hashTable.deleter
    def hashTable(self: "hashMap") -> NoReturn:
        raise ValueError("read-only.")

    @property
    def keys(self: "hashMap") -> List:
        """X.keys -> a set-like object providing a view on X's keys."""
        return self._keys

    @keys.setter
    def keys(self: "hashMap", data: List) -> NoReturn:
        raise ValueError("read-only.")

    @keys.deleter
    def keys(self: "hashMap") -> NoReturn:
        raise ValueError("read-only.")

    @property
    def values(self: "hashMap") -> List:
        """X.values -> an object providing a view on X's values."""
        return self._values

    @values.setter
    def values(self: "hashMap", data: List) -> NoReturn:
        raise ValueError("read-only.")

    @values.deleter
    def values(self: "hashMap") -> NoReturn:
        raise ValueError("read-only.")

    @property
    def items(
        self: "hashMap",
    ) -> List:
        """X.items -> a set-like object providing a view on X's items."""
        return self._items

    @items.setter
    def items(self: "hashMap", data: List) -> NoReturn:
        raise ValueError("read-only.")

    @items.deleter
    def items(self: "hashMap") -> NoReturn:
        raise ValueError("read-only.")

    def get_linked_list(
        self: "hashMap", index: int | str
    ) -> singlyLinkedList | None | NoReturn:
        if isinstance(index, int):
            if 26 > index >= 0:
                if self.hashTable[index] is not None:
                    x: singlyLinkedList = singlyLinkedList(detail=self.detail)
                    x._head = self.hashTable[index]
                    return x
            else:
                raise IndexError("Hash table index out of range.")
        elif isinstance(index, str):
            if len(index) == 1:
                if "a" <= index <= "z":
                    return self.get_linked_list(ord(index) - 97)
                elif "A" <= index <= "Z":
                    return self.get_linked_list(ord(index) - 65)
                else:
                    try:
                        return self.get_linked_list(int(index))
                    except ValueError as e3:
                        raise IndexError("Hash table index out of range.") from None
            else:
                try:
                    return self.get_linked_list(int(index))
                except ValueError as e4:
                    raise TypeError("Only characters accepted.") from None
        else:
            raise TypeError("Only integers and characters accepted.")

    def clear(self: "hashMap") -> None:
        if self.len > 0:
            self._hashTable: List = [None] * 26
            self._keys: List = []
            self._values: List = []
            self._items: List = []
            self.len: int = 0

    def fromkeys(self: "hashMap", iterable: Iterable[Any], value: Any = None) -> Self:
        """Create a new dictionary with keys from iterable and values set to value."""
        try:
            x: Iterator = iter(iterable)  # convert iterable to iterator
            try:
                if len(value) == len(iterable) and not isinstance(value, str):
                    y: Iterator = iter(value)
                else:
                    y: bool = False
            except TypeError as e5:
                y: bool = False
            while True:
                self[next(x)] = value if not y else next(y)
        except TypeError as e6:
            raise TypeError(f"{iterable} is not iterable.") from None
        except StopIteration as e7:
            return self

    def get(
        self: "hashMap",
        key: int | float | complex | str | Tuple | None,
        default: Any = None,
    ) -> Any:
        """Return the value for key if key is in the dictionary, else default."""
        try:
            return self[key]
        except KeyError as e8:
            return default

    def copy(self: "hashMap") -> "hashMap":
        """X.copy() -> a shallow copy of X."""
        return hashMap(self._items, detail=self.detail)

    def pop(
        self: "hashMap",
        key: int | float | complex | str | Tuple | None,
        default: Any = _sentinel,
    ) -> Any:
        """X.pop(k[,d]) -> v, remove specified key and return the corresponding value.

        If the key is not found, return the default if given; otherwise, raise a KeyError.
        """
        try:
            returned_value: Any = self[key]
            del self[key]
            return returned_value
        except KeyError as e9:
            if default is _sentinel:
                raise e9
            return default

    def popitem(
        self: "hashMap",
    ) -> Tuple[int | float | complex | str | Tuple | None, Any]:
        if self.len > 0:
            return_value: Tuple = self._items[-1]
            del self[self._keys[-1]]
            return return_value
        raise KeyError("popitem(): hashMap is empty.")

    def setdefault(
        self: "hashMap",
        key: int | float | complex | str | Tuple | None,
        value: Any = None,
    ) -> None | NoReturn:
        self[key] = value

    def update(self: "hashMap", hash_map: "hashMap") -> None | NoReturn:
        if not isinstance(hash_map, hashMap):
            raise TypeError("Only a hashMap object is acceptable.")
        for item in hash_map.items:
            self[item[0]] = item[1]

    def __or__(self: "hashMap", other: "hashMap") -> "hashMap" | NoReturn:
        if not isinstance(other, hashMap):
            raise TypeError("Only a hashMap object is acceptable.")
        x: hashMap = self.copy()
        x.update(other)
        return x

    def __ior__(self: "hashMap", other: "hashMap") -> "hashMap" | NoReturn:
        return self.__or__(other)

    def __len__(self: "hashMap") -> int:
        return self.len

    def __setitem__(
        self: "hashMap", key: int | float | complex | str | Tuple | None, value: Any
    ) -> None | NoReturn:
        self.__hash_table([[key, value]])

    def __getitem__(self: "hashMap", index: int | float | str | complex | None) -> Any:
        ascii_sum: int = self.__hash_function(index) % 26
        head: _singlyLinkedListNode = self._hashTable[ascii_sum]
        try:
            if head.data[0] == index:
                return head.data[1]
            else:
                head: _singlyLinkedListNode | None = head.next
                while head:
                    if head.data[0] == index:
                        return head.data[1]
                    head: _singlyLinkedListNode | None = head.next
                else:
                    raise KeyError(f"{index}")
        except AttributeError as e10:
            try:
                return self._keys[index]
            except IndexError as e11:
                raise KeyError(index) from None

    def __delitem__(
        self: "hashMap", key: int | float | complex | str | Tuple | None
    ) -> None | NoReturn:
        try:
            index: int = self._keys.index(key)
            self._keys.remove(key)
            self._values.remove(self._values[index])
            self._items.remove(self._items[index])
            self.len -= 1
            hash_table_index: int = self.__hash_function(key) % 26
            head: _singlyLinkedListNode = self._hashTable[hash_table_index]
            helper: None = None
            while head:
                if head.data[0] is key and helper is None and head.next is None:
                    self._hashTable[hash_table_index] = None
                    del head
                    break
                elif head.data[0] is key and helper is None and head.next is not None:
                    self._hashTable[hash_table_index] = head.next
                    head.next = None
                    del head
                    break
                elif head.data[0] is key and helper is not None and head.next is None:
                    helper.next = None
                    del head
                    break
                elif (
                    head.data[0] is key and helper is not None and head.next is not None
                ):
                    helper.next = head.next
                    head.next = None
                    del head
                    break
                else:
                    helper: _singlyLinkedListNode = head
                    head: _singlyLinkedListNode | None = head.next
        except ValueError as e12:
            raise KeyError(f"{key}") from None

    def __iter__(self: "hashMap") -> Iterator:
        return iter(self._keys)

    def __str__(self: "hashMap") -> str:
        if self.len == 0:
            return "{}"
        output: List = []
        if not self.detail:
            try:
                for i in range(len(self._keys)):
                    if not isinstance(self._keys[i], str) and not isinstance(
                        self._values[i], str
                    ):
                        output.append(f"{self._keys[i]}: {self._values[i]}")
                    elif not isinstance(self._keys[i], str) and isinstance(
                        self._values[i], str
                    ):
                        if len(self._values[i]) == 0:
                            output.append(f"{self._keys[i]}: {self._values[i]}")
                        elif len(self._values[i]) == 1:
                            output.append(f"{self._keys[i]}: '{self._values[i]}'")
                        else:
                            output.append(f'{self._keys[i]}: "{self._values[i]}"')
                    elif isinstance(self._keys[i], str) and not isinstance(
                        self._values[i], str
                    ):
                        if len(self._keys[i]) == 0:
                            output.append(f"{self._keys[i]}: {self._values[i]}")
                        elif len(self._keys[i]) == 1:
                            output.append(f"'{self._keys[i]}': {self._values[i]}")
                        else:
                            output.append(f'"{self._keys[i]}": {self._values[i]}')
                    else:
                        if len(self._keys[i]) == 0 and len(self._values[i]) == 0:
                            output.append(f"{self._keys[i]}: {self._values[i]}")
                        elif len(self._keys[i]) == 1 and len(self._values[i]) == 0:
                            output.append(f"'{self._keys[i]}': {self._values[i]}")
                        elif len(self._keys[i]) > 1 and len(self._values[i]) == 0:
                            output.append(f'"{self._keys[i]}": {self._values[i]}')
                        elif len(self._keys[i]) == 0 and len(self._values[i]) == 1:
                            output.append(f"{self._keys[i]}: '{self._values[i]}'")
                        elif len(self._keys[i]) == 1 and len(self._values[i]) == 1:
                            output.append(f"'{self._keys[i]}': '{self._values[i]}'")
                        elif len(self._keys[i]) > 1 and len(self._values[i]) == 1:
                            output.append(f"\"{self._keys[i]}\": '{self._values[i]}'")
                        elif len(self._keys[i]) == 0 and len(self._values[i]) > 1:
                            output.append(f'{self._keys[i]}: "{self._values[i]}"')
                        elif len(self._keys[i]) == 1 and len(self._values[i]) > 1:
                            output.append(f"'{self._keys[i]}': \"{self._values[i]}\"")
                        else:
                            output.append(f'"{self._keys[i]}": "{self._values[i]}"')
                output[0] = "{" + output[0]
                output[-1] += "}"
                return ", ".join(output)
            except IndexError as e13:
                raise TypeError("Invalid data type.") from None
        else:
            if self.len > 0:
                print(
                    _white("Hash function :")
                    + "\n"
                    + _white("_" * len("Hash function") + "\n")
                )
                print(
                    _white("f(")
                    + _blue("x")
                    + _white(") = ")
                    + _green("ord(")
                    + _blue("x")
                    + _green(") ")
                    + _red("% ")
                    + _blue("N ")
                    + _white("(Hash table capacity)")
                    + "\n"
                )
                print(_white("Example :") + "\n" + _white("_" * len("Example")) + "\n")
                print(
                    _blue("N ")
                    + _white("= 26")
                    + "\n\n"
                    + _white("f(")
                    + _blue('"ABC"')
                    + _white(") = ")
                    + _green("ord(")
                    + _blue('"ABC"')
                    + _green(")")
                    + _red(" % ")
                    + _white("26 = (")
                    + _green("ord(")
                    + _blue("'A'")
                    + _green(") ")
                    + _white("+ ")
                    + _green("ord(")
                    + _blue("'B'")
                    + _green(") ")
                    + _white("+ ")
                    + _green("ord(")
                    + _blue("'C'")
                    + _green(")")
                    + _white(") ")
                    + _red("% ")
                    + _white("26 = (65 + 66 + 67) ")
                    + _red("% ")
                    + _white("26 = 198 ")
                    + _red("% ")
                    + _white("26 = 16")
                    + "\n\n"
                    + _white("The value associated with the key ")
                    + _blue('"ABC" ')
                    + _white(
                        "will be placed at index 16 in the hash table (array) with a capacity of 26."
                    )
                    + "\n"
                )
                print(
                    _white("Notes :")
                    + "\n"
                    + _white("_" * len("Notes"))
                    + "\n\n"
                    + _white(
                        "- If a key has the same index as an existing key in the hash table, it will be placed after it because, in a hash table, each index is a linked list."
                    )
                    + "\n\n"
                    + _white(
                        "- If a key is duplicated in the hash table, the last value associated with this key will be saved."
                    )
                    + "\n"
                )
                print(
                    _white("Hash Table :")
                    + "\n"
                    + _white("_" * len("Hash Table"))
                    + "\n"
                )
                output.append(
                    [
                        _white("Key"),
                        _white("Hash function Output (Index)"),
                        _white("Value"),
                    ]
                )
            for i in range(len(self._keys)):
                output.append(
                    [
                        (
                            _blue(f"{self._keys[i]}")
                            if not isinstance(self._keys[i], str)
                            else (
                                _blue(f"{self._keys[i]}")
                                if len(self._keys[i]) == 0
                                else (
                                    _blue(f"'{self._keys[i]}'")
                                    if len(self._keys[i]) == 1
                                    else _blue(f'"{self._keys[i]}"')
                                )
                            )
                        ),
                        _green(f"{self.__hash_function(self._keys[i]) % 26}"),
                        (
                            _cyan(f"{self._values[i]}")
                            if not isinstance(self._values[i], str)
                            else (
                                _cyan(f"{self._values[i]}")
                                if len(self._values[i]) == 0
                                else (
                                    _cyan(f"'{self._values[i]}'")
                                    if len(self._values[i]) == 1
                                    else _cyan(f'"{self._values[i]}"')
                                )
                            )
                        ),
                    ]
                )
            return tabulate(output, headers="firstrow", tablefmt="fancy_grid")


def _main() -> None:
    print("hashtbl")


if __name__ == "__main__":
    _main()
