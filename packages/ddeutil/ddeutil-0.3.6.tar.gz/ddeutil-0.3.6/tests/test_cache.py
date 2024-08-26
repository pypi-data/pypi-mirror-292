import ddeutil.core.__base.cache as cache


def test_memoize():
    @cache.memoize
    def fib(n):
        if n in (0, 1):
            return 1
        return fib(n - 1) + fib(n - 2)

    assert fib.cache == {}

    for i in range(3):
        fib(i)

    assert fib.cache == {"(0,){}": 1, "(1,){}": 1, "(2,){}": 2}
