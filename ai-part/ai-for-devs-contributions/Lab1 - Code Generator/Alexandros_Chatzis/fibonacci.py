def calculate_fibonacci(start: int, end: int) -> list[int]:
    """
    Calculate Fibonacci numbers in a specified range.

    Args:
        start (int): The starting index of the Fibonacci sequence (inclusive).
        end (int): The ending index of the Fibonacci sequence (inclusive).

    Returns:
        list[int]: A list of Fibonacci numbers from the start index to the end index.

    Raises:
        ValueError: If start or end is not a non-negative integer, or if start > end.

    Example:
        >>> calculate_fibonacci(0, 5)
        [0, 1, 1, 2, 3, 5]
    """
    if not isinstance(start, int) or not isinstance(end, int):
        raise ValueError("Both start and end must be integers.")
    if start < 0 or end < 0:
        raise ValueError("Both start and end must be non-negative integers.")
    if start > end:
        raise ValueError("Start index must be less than or equal to end index.")

    fibonacci_sequence = []
    a, b = 0, 1

    for index in range(end + 1):
        if index >= start:
            fibonacci_sequence.append(a)
        a, b = b, a + b

    return fibonacci_sequence