import ddeutil.core.__base.sorting as sorting


def test_ordered():
    result = sorting.ordered([[11], [2], [4, 1]])
    respect = [[1, 4], [2], [11]]
    for i in range(3):
        assert result[i] == respect[i]
