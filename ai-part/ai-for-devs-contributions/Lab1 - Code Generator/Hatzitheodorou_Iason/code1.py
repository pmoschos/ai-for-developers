def sum_of_squares_of_evens(numbers: list) -> int:
    """
    Calculate the sum of the squares of the even numbers in the given list.

    Args:
        numbers (list): A list of numbers (integers or floats).

    Returns:
        int: The sum of the squares of the even numbers.

    Raises:
        ValueError: If the input is not a list or contains non-numeric elements.
    """
    if not isinstance(numbers, list):
        raise ValueError("Input must be a list.")
    
    sum_squares = 0
    for num in numbers:
        if not isinstance(num, (int, float)):
            raise ValueError("List must contain only numeric elements.")
        if num % 2 == 0:
            sum_squares += num ** 2
            
    return sum_squares