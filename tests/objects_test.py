import pytest

from prymate import objects


@pytest.mark.parametrize(
    "str1, str2, should_match",
    [
        ("Hello World", "Hello World", True),
        ("My name is johnny", "My name is johnny", True),
        ("Hello World", "My name is johnny", False),
        ("Hello World", "My name is johnny", False),
    ],
)
def test_string_hash(str1: str, str2: str, should_match: bool) -> None:
    obj1 = objects.String(str1)
    obj2 = objects.String(str2)

    if should_match:
        assert hash(obj1) == hash(obj2)
    else:
        assert hash(obj1) != hash(obj2)
