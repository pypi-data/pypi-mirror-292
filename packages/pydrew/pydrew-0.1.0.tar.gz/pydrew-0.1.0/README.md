# pydrew
A set of tool for python projects

## Custom List Implementation

This repository contains a custom generic list implementation called `List`, which provides additional functionality beyond the built-in Python list. This class is designed using Python's type hinting capabilities to support type safety and offers various utility methods for list manipulation.

## Features

- Generic list implementation capable of handling any type `T`.
- Additional methods for enhanced list operations such as `concat`, `removeAt`, `where`, `group_by`, and more.
- Magic methods to support intuitive Pythonic operations like indexing, iteration, and concatenation.
- Ability to convert the list to different formats such as Python's native list or a dictionary.
- Includes methods to sort, filter, map, and group list elements based on conditions or properties.

## Usage

### Initialization

You can initialize a `List` in a few different ways:
```python
from your_module import List

# Initialize an empty list
my_list = List()

# Initialize from a Python list
my_list = List([1, 2, 3])

# Initialize from an iterator
my_list = List(iter([1, 2, 3]))
```

### Basic Operations
```python
my_list.add(4)          # Add 4 to the list
my_list.add(5, index=1) # Add 5 at index 1

my_list.remove(4)       # Remove the first occurrence of 4
my_list.remove_at(1)    # Remove element at index 1

first_item = my_list.first()  # Get the first element
last_item = my_list.last()    # Get the last element
item = my_list.at_index(2)    # Get element at index 2
```

### Advanced Operations
```python
even_numbers = my_list.where(lambda x: x % 2 == 0) # Filter even numbers
squares = my_list.select(lambda x: x ** 2)         # Square each element

sorted_list = my_list.sort(lambda x: x)            # Sort ascending
grouped = my_list.group_by('attribute')            # Group by object attribute

my_list.reverse()      # Reverse the list
my_list.clear()        # Clear all elements from the list
length = my_list.count() # Get the number of elements
python_list = my_list.to_list() # Convert to Python list

### Magic Methods
```python
another_list = List([6, 7, 8])
combined_list = my_list + another_list
difference_list = my_list - List([3, 4])
````


This README provides a comprehensive overview of the class, including initialization, basic and advanced operations, usage examples, and contribution guidelines. If the code is part of a larger module, you should replace `your_module` with the actual module name when importing.
