from prymate import objects


def test_string_hash():
    hello1 = objects.String("Hello World")
    hello2 = objects.String("Hello World")

    diff1 = objects.String("My name is johnny")
    diff2 = objects.String("My name is johnny")

    assert hash(hello1) == hash(hello2)
    assert hash(diff1) == hash(diff2)
    assert hash(hello1) != hash(diff1)
    assert hash(hello2) != hash(diff2)
