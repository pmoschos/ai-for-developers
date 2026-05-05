## Prompt Quality

Generating code for: ``a sort function``

```python
=== Generated Code ===
from typing import List, Any

def sort_list(input_list: List[Any]) -> List[Any]:
    """
    Sorts a list in ascending order.

    Args:
        input_list (List[Any]): The list to be sorted.

    Returns:
        List[Any]: A new list containing the sorted elements.

    Example:
        >>> sort_list([3, 1, 2])
        [1, 2, 3]
    """
    if not isinstance(input_list, list):
        raise ValueError("Input must be a list.")

    # Using the built-in sorted function to sort the list
    return sorted(input_list)
```


Generating code for: ``a function that implements quicksort with in-place partitioning for a list of integers``

```python
=== Generated Code ===
from typing import List

def quicksort(arr: List[int]) -> List[int]:
    """
    Sorts a list of integers in-place using the quicksort algorithm.

    Args:
        arr (List[int]): The list of integers to be sorted.

    Returns:
        List[int]: The sorted list of integers.

    Example:
        >>> quicksort([3, 6, 8, 10, 1, 2, 1])
        [1, 1, 2, 3, 6, 8, 10]
    """
    if not isinstance(arr, list):
        raise ValueError("Input must be a list.")
    if not all(isinstance(x, int) for x in arr):
        raise ValueError("All elements in the list must be integers.")

    def partition(low: int, high: int) -> int:
        pivot = arr[high]  # Choosing the last element as pivot
        i = low - 1  # Pointer for the smaller element

        for j in range(low, high):
            if arr[j] < pivot:  # If current element is smaller than or equal to pivot
                i += 1
                arr[i], arr[j] = arr[j], arr[i]  # Swap elements

        arr[i + 1], arr[high] = arr[high], arr[i + 1]  # Place pivot in the correct position
        return i + 1

    def quicksort_recursive(low: int, high: int) -> None:
        if low < high:
            pi = partition(low, high)  # Partitioning index
            quicksort_recursive(low, pi - 1)  # Recursively sort elements before partition
            quicksort_recursive(pi + 1, high)  # Recursively sort elements after partition

    quicksort_recursive(0, len(arr) - 1)  # Initial call to the recursive quicksort function
    return arr
```

**Findings** : The more detailed approach:
- is tailored to integer sorting only, not all data types
- the sorting method was determined explicitly, instead of simply using the built in sorted() func
- has better error handling (includes items inside the list)



## Temperature Impact

### Temp = 0.2
   
```python
# ── Παράδειγμα 1: Απλή δημιουργία ──
# Generating code for: a function that finds prime numbers up to n
# === Generated Code ===
from typing import List

def find_prime_numbers(up_to: int) -> List[int]:
    """
    Find all prime numbers up to a given number.

    Args:
        up_to (int): The upper limit (inclusive) to find prime numbers.

    Returns:
        List[int]: A list of prime numbers up to the specified limit.

    Example:
        >>> find_prime_numbers(10)
        [2, 3, 5, 7]
    """
    if up_to < 2:
        return []

    prime_numbers = []
    for number in range(2, up_to + 1):
        is_prime = True
        for divisor in range(2, int(number**0.5) + 1):
            if number % divisor == 0:
                is_prime = False
                break
        if is_prime:
            prime_numbers.append(number)

    return prime_numbers

# ==================================================

# ── Παράδειγμα 2: Με tests (Prompt Chaining) ──
# Generating code for: merge two sorted lists
# === Generated Code ===
from typing import List

def merge_sorted_lists(list1: List[int], list2: List[int]) -> List[int]:
    """
    Merges two sorted lists into a single sorted list.

    Args:
        list1 (List[int]): The first sorted list.
        list2 (List[int]): The second sorted list.

    Returns:
        List[int]: A new sorted list containing all elements from both input lists.

    Example:
        >>> merge_sorted_lists([1, 3, 5], [2, 4, 6])
        [1, 2, 3, 4, 5, 6]
    """
    if not isinstance(list1, list) or not isinstance(list2, list):
        raise ValueError("Both inputs must be lists.")

    merged_list = []
    index1, index2 = 0, 0

    # Merge the two lists while maintaining sorted order
    while index1 < len(list1) and index2 < len(list2):
        if list1[index1] < list2[index2]:
            merged_list.append(list1[index1])
            index1 += 1
        else:
            merged_list.append(list2[index2])
            index2 += 1

    # Append any remaining elements from list1
    while index1 < len(list1):
        merged_list.append(list1[index1])
        index1 += 1

    # Append any remaining elements from list2
    while index2 < len(list2):
        merged_list.append(list2[index2])
        index2 += 1

    return merged_list

# === Unit Tests ===
import unittest

class TestMergeSortedLists(unittest.TestCase):

    def test_merge_two_non_empty_sorted_lists(self):
        """Test merging two non-empty sorted lists."""
        self.assertEqual(merge_sorted_lists([1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6])

    def test_merge_with_one_empty_list(self):
        """Test merging a non-empty sorted list with an empty list."""
        self.assertEqual(merge_sorted_lists([1, 2, 3], []), [1, 2, 3])
        self.assertEqual(merge_sorted_lists([], [4, 5, 6]), [4, 5, 6])

    def test_merge_two_empty_lists(self):
        """Test merging two empty lists."""
        self.assertEqual(merge_sorted_lists([], []), [])

    def test_merge_sorted_lists_with_duplicates(self):
        """Test merging two sorted lists that contain duplicates."""
        self.assertEqual(merge_sorted_lists([1, 2, 2], [2, 3, 4]), [1, 2, 2, 2, 3, 4])

    def test_merge_sorted_lists_with_invalid_input(self):
        """Test merging with invalid inputs."""
        with self.assertRaises(ValueError):
            merge_sorted_lists([1, 2, 3], "not_a_list")
        with self.assertRaises(ValueError):
            merge_sorted_lists("not_a_list", [1, 2, 3])
        with self.assertRaises(ValueError):
            merge_sorted_lists(None, [1, 2, 3])
        with self.assertRaises(ValueError):
            merge_sorted_lists([1, 2, 3], None)

if __name__ == '__main__':
    unittest.main()

# ==================================================

# ── Παράδειγμα 3: Με αποθήκευση σε αρχείο ──
# Generating code for: calculate fibonacci
# === Generated Code ===
def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.

    Args:
        n (int): The position in the Fibonacci sequence (0-indexed).

    Returns:
        int: The nth Fibonacci number.

    Example:
        >>> calculate_fibonacci(5)
        5
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    elif n == 0:
        return 0
    elif n == 1:
        return 1

    # Initialize the first two Fibonacci numbers
    previous, current = 0, 1

    # Calculate Fibonacci iteratively
    for _ in range(2, n + 1):
        previous, current = current, previous + current

    return current
# Saved to C:\Users\georf\Desktop\AI for Developers\labs\code_generator\fibonacci.py
```
### Temp = 0.9

```python
# ── Παράδειγμα 1: Απλή δημιουργία ──
# Generating code for: a function that finds prime numbers up to n
# === Generated Code ===
from typing import List

def find_prime_numbers(up_to: int) -> List[int]:
    """
    Finds all prime numbers up to a specified number.

    Args:
        up_to (int): The upper limit (inclusive) for finding prime numbers.

    Returns:
        List[int]: A list of prime numbers up to the specified limit.

    Example:
        >>> find_prime_numbers(10)
        [2, 3, 5, 7]
    """
    if up_to < 2:
        return []  # No primes below 2

    prime_numbers = []
    for candidate in range(2, up_to + 1):
        is_prime = True
        for divisor in range(2, int(candidate**0.5) + 1):
            if candidate % divisor == 0:
                is_prime = False
                break  # Found a divisor, not prime
        if is_prime:
            prime_numbers.append(candidate)

    return prime_numbers

# ==================================================

# ── Παράδειγμα 2: Με tests (Prompt Chaining) ──
# Generating code for: merge two sorted lists
# === Generated Code ===
from typing import List

def merge_sorted_lists(list_one: List[int], list_two: List[int]) -> List[int]:
    """
    Merges two sorted lists into a single sorted list.

    Args:
        list_one (List[int]): The first sorted list.
        list_two (List[int]): The second sorted list.

    Returns:
        List[int]: A merged sorted list containing all elements from both input lists.

    Example:
        >>> merge_sorted_lists([1, 3, 5], [2, 4, 6])
        [1, 2, 3, 4, 5, 6]
    """
    try:
        merged_list = []
        index_one, index_two = 0, 0

        # Iterate through both lists until we reach the end of one
        while index_one < len(list_one) and index_two < len(list_two):
            if list_one[index_one] < list_two[index_two]:
                merged_list.append(list_one[index_one])
                index_one += 1
            else:
                merged_list.append(list_two[index_two])
                index_two += 1

        # Append any remaining elements from list_one
        while index_one < len(list_one):
            merged_list.append(list_one[index_one])
            index_one += 1

        # Append any remaining elements from list_two
        while index_two < len(list_two):
            merged_list.append(list_two[index_two])
            index_two += 1

        return merged_list

    except TypeError as e:
        raise ValueError("Both inputs must be lists of integers.") from e

# === Unit Tests ===
import unittest

class TestMergeSortedLists(unittest.TestCase):

    def test_merge_two_sorted_lists(self):
        """Test merging two sorted lists with distinct elements."""
        self.assertEqual(merge_sorted_lists([1, 3, 5], [2, 4, 6]), [1, 2, 3, 4, 5, 6])

    def test_merge_sorted_lists_with_common_elements(self):
        """Test merging two sorted lists with some common elements."""
        self.assertEqual(merge_sorted_lists([1, 2, 3], [2, 3, 4]), [1, 2, 2, 3, 3, 4])

    def test_merge_empty_lists(self):
        """Test merging two empty lists."""
        self.assertEqual(merge_sorted_lists([], []), [])

    def test_merge_list_with_empty_and_non_empty(self):
        """Test merging a non-empty list with an empty list."""
        self.assertEqual(merge_sorted_lists([], [1, 2, 3]), [1, 2, 3])
        self.assertEqual(merge_sorted_lists([4, 5, 6], []), [4, 5, 6])

    def test_merge_lists_with_negative_numbers(self):
        """Test merging two sorted lists that include negative numbers."""
        self.assertEqual(merge_sorted_lists([-3, -1, 0], [-2, 1, 2]), [-3, -2, -1, 0, 1, 2])

    def test_merge_lists_with_invalid_inputs(self):
        """Test that merging non-list inputs raises a ValueError."""
        with self.assertRaises(ValueError):
            merge_sorted_lists([1, 2, 3], None)
        with self.assertRaises(ValueError):
            merge_sorted_lists(None, [1, 2, 3])
        with self.assertRaises(ValueError):
            merge_sorted_lists("not_a_list", [1, 2, 3])
        with self.assertRaises(ValueError):
            merge_sorted_lists([1, 2, 3], "not_a_list")

if __name__ == "__main__":
    unittest.main()

# ==================================================

# ── Παράδειγμα 3: Με αποθήκευση σε αρχείο ──
# Generating code for: calculate fibonacci
# === Generated Code ===
def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.

    Args:
        n (int): The position in the Fibonacci sequence to calculate (0-indexed).

    Returns:
        int: The nth Fibonacci number.

    Example:
        >>> calculate_fibonacci(5)
        5
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")

    # Base cases for the Fibonacci sequence
    if n == 0:
        return 0
    elif n == 1:
        return 1

    # Using iterative approach to compute Fibonacci number for efficiency
    previous, current = 0, 1
    for _ in range(2, n + 1):
        previous, current = current, previous + current

    return current
# Saved to C:\Users\georf\Desktop\AI for Developers\labs\code_generator\fibonacci.py
```

**Findings**: The only difference between 2 temperatures was the different naming of variables and different comments. The core functionality remains the same.