# hashtbl


[![PyPI version](https://badge.fury.io/py/hashtbl.svg)](https://badge.fury.io/py/hashtbl)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


This library was created to simplify the concept of a hash table and explain how it works in the background in a clear and simple way, especially for beginners in data structures.


## Installation


You can install `hashtbl` via pip:


```bash
pip install hashtbl
```


## Usage 


```python
from hashtbl import hashMap


x = hashMap(
    [
        ["key1", "value1"],
        ["key2", "value2"],
        ["key3", "value3"],
    ]
)


print(x)
```


### Output


```bash
{"key1": "value1", "key2": "value2", "key3": "value3"}
```


#### You Can Show All Details


```python
from hashtbl import hashMap


x = hashMap(
    [
        ["key1", "value1"],
        ["key2", "value2"],
        ["key3", "value3"],
    ],
    detail=True,
)


print(x)
```


### Output


```bash
Hash function :
_____________

f(x) = ord(x) % N (Hash table capacity)

Example :
_______

N = 26

f("ABC") = ord("ABC") % 26 = (ord('A') + ord('B') + ord('C')) % 26 = (65 + 66 + 67) % 26 = 198 % 26 = 16

The value associated with the key "ABC" will be placed at index 16 in the hash table (array) with a capacity of 26.

Notes :
_____

- If a key has the same index as an existing key in the hash table, it will be placed after it because, in a hash table, each index is a linked list.

- If a key is duplicated in the hash table, the last value associated with this key will be saved.

Hash Table :
__________

╒════════╤════════════════════════════════╤══════════╕
│ Key    │   Hash function Output (Index) │ Value    │
╞════════╪════════════════════════════════╪══════════╡
│ "key1" │                             14 │ "value1" │
├────────┼────────────────────────────────┼──────────┤
│ "key2" │                             15 │ "value2" │
├────────┼────────────────────────────────┼──────────┤
│ "key3" │                             16 │ "value3" │
╘════════╧════════════════════════════════╧══════════╛
```


## Advanced Usage


#### You Can See The Key/Value Pairs In The Linked List If There Is More Than One Key In One Index (Hash Function Output).


```python
from hashtbl import hashMap


x = hashMap(
    [
        ["algorithm", "algo"],
        ["logarithm", "log"],
    ],
    detail=False,
)


# When the keys are 'algorithm' and 'logarithm', 5 is the output index of the hash function. You can view this index and all other key indexes by printing with all details (detail=True).
print(x.get_linked_list(5))
```


### Output


```bash
[('algorithm', 'algo')] -> [('logarithm', 'log')] -> None (NULL)
```


#### You Can See It With All Details


```python
from hashtbl import hashMap


x = hashMap(
    [
        ["algorithm", "algo"],
        ["logarithm", "log"],
    ],
    detail=True,
)


# When the keys are 'algorithm' and 'logarithm', 5 is the output index of the hash function. You can view this index and all other key indexes by printing with all details (detail=True).
print(x.get_linked_list(5))
```


### Output


```bash
╒═══════════════════════╤═════════════════════════╤══════════════════════╤══════════════════════╕
│ Current Value         │ Current Value @ddress   │ Next Value           │ Next Value @ddress   │
╞═══════════════════════╪═════════════════════════╪══════════════════════╪══════════════════════╡
│ ('algorithm', 'algo') │ 0x7f527dd225d0          │ ('logarithm', 'log') │ 0x7f527dd21d50       │
├───────────────────────┼─────────────────────────┼──────────────────────┼──────────────────────┤
│ ('logarithm', 'log')  │ 0x7f527dd21d50          │ None (NULL)          │ 0x95bcc0 (nil/0x0)   │
├───────────────────────┼─────────────────────────┼──────────────────────┼──────────────────────┤
│ None (NULL)           │ 0x95bcc0 (nil/0x0)      │                      │                      │
╘═══════════════════════╧═════════════════════════╧══════════════════════╧══════════════════════╛
```


### Note


You can use all methods of the built-in hash table (dictionary) with this custom hash table.


## License


This project is licensed under the MIT LICENSE - see the [LICENSE](https://opensource.org/licenses/MIT) for more details.
