from ddeutil.core.__base.hash import (
    checksum,
    hash_all,
    hash_pwd,
    hash_str,
    same_pwd,
    tokenize,
)


def test_tokenize():
    assert tokenize("Hello") == tokenize("Hello")
    assert "9d71491b50023b06fc76928e6eddb952" == tokenize([1, 2, "3"])
    assert "1b94fd88ee7c12484422d1715818bf1f" == tokenize(1, 2, foo="bar")


def test_pwd():
    s, pw = hash_pwd("P@ssW0rd")
    assert same_pwd(s, pw, "P@ssW0rd")


def test_hash_str():
    assert "05751529" == hash_str("hello world")
    assert "105751529" == hash_str("hello world", n=9)


def test_hash_all():
    assert {
        "dict": {
            "list": [
                "acbd18db4cc2f85cedef654fccc4a4d8",
                "37b51d194a7513e45b56f6524f2d51f2",
            ]
        },
        "bool": True,
        "none": None,
        "str": "acbd18db4cc2f85cedef654fccc4a4d8",
        "tuple": (
            "c4ca4238a0b923820dcc509a6f75849b",
            "c81e728d9d4c2f636f067f89cc14862c",
            "eccbc87e4b5ce2fe28308fd9f2a7baf3",
        ),
    } == hash_all(
        {
            "str": "foo",
            "bool": True,
            "none": None,
            "tuple": (
                1,
                2,
                3,
            ),
            "dict": {
                "list": ["foo", "bar"],
            },
        }
    )


def test_checksum():
    assert "83788ce748a5899920673e5a4384979b" == checksum(
        {"foo": "bar", "baz": 1}
    )
