import ddeutil.core.__base.splitter as split


def test_rsplit():
    assert ["foo", "bar"] == split.must_rsplit(
        "foo bar", maxsplit=2, mustsplit=False
    )
