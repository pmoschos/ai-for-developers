"""Example generated function and pytest tests."""

import pytest


def make_function() -> None:
    """Create a placeholder function that raises ``NotImplementedError``."""
    raise NotImplementedError("This function is a placeholder and is not implemented.")


def test_make_function_raises_not_implemented_error() -> None:
    """Verify that the placeholder function raises the expected exception."""
    with pytest.raises(NotImplementedError) as exc_info:
        make_function()
    assert str(exc_info.value) == "This function is a placeholder and is not implemented."


def test_make_function_type_hint() -> None:
    """Verify that the function exposes the expected return annotation."""
    assert make_function.__annotations__ == {"return": None}


def test_make_function_no_parameters() -> None:
    """Verify that the function does not accept any parameters."""
    assert make_function.__code__.co_argcount == 0


def test_make_function_docstring() -> None:
    """Verify that the function includes a descriptive docstring."""
    assert make_function.__doc__ is not None
    assert "placeholder function" in make_function.__doc__


def test_make_function_function_object() -> None:
    """Verify that the generated object is callable."""
    assert callable(make_function)
