# Code Generator CLI - Usage Examples

## Basic Usage

### Generate a simple function
```bash
python code_generator.py "a function that calculates the factorial of a number"
```

### Generate with unit tests
```bash
python code_generator.py "a function that reverses a string" --with-tests
```

### Save to file
```bash
python code_generator.py "binary search in a sorted list" --save binary_search.py
```

### Combine options
```bash
python code_generator.py "merge sort algorithm" --with-tests --save merge_sort.py
```

### Interactive mode
```bash
python code_generator.py -i
```

## Example Generated Code

### Input
```
"a function that finds all prime numbers up to n using the Sieve of Eratosthenes"
```

### Output
```python
def sieve_of_eratosthenes(n: int) -> list[int]:
    """
    Find all prime numbers up to n using the Sieve of Eratosthenes algorithm.
    
    Args:
        n: The upper limit (inclusive) to find primes up to.
        
    Returns:
        A list of all prime numbers from 2 to n.
        
    Example:
        >>> sieve_of_eratosthenes(20)
        [2, 3, 5, 7, 11, 13, 17, 19]
        >>> sieve_of_eratosthenes(2)
        [2]
        >>> sieve_of_eratosthenes(1)
        []
    """
    if n < 2:
        return []
    
    # Create a boolean array "is_prime[0..n]" and initialize all entries as true
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    
    # Start with the first prime number, 2
    p = 2
    while p * p <= n:
        # If is_prime[p] is not changed, then it is a prime
        if is_prime[p]:
            # Update all multiples of p
            for i in range(p * p, n + 1, p):
                is_prime[i] = False
        p += 1
    
    # Collect all prime numbers
    return [i for i in range(2, n + 1) if is_prime[i]]
```

## Tips for Better Results

1. **Be specific**: "a function that sorts a list" → "a function that implements quicksort with in-place partitioning"

2. **Mention edge cases**: "a function that divides two numbers and handles division by zero"

3. **Specify return types**: "a function that returns a tuple of (success: bool, message: str)"

4. **Include constraints**: "a function that finds duplicates in O(n) time complexity"

5. **Reference algorithms**: "a function that implements Dijkstra's shortest path algorithm"
