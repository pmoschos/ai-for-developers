def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number.

    Args:
        n (int): The index of the Fibonacci number to calculate (0-based).

    Returns:
        int: The nth Fibonacci number.

    Example:
        >>> calculate_fibonacci(5)
        5
        >>> calculate_fibonacci(0)
        0
        >>> calculate_fibonacci(1)
        1
    """
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")

    if n == 0:
        return 0
    elif n == 1:
        return 1
    
    previous, current = 0, 1
    # Iteratively calculate Fibonacci numbers up to n
    for _ in range(2, n + 1):
        previous, current = current, previous + current

    return current