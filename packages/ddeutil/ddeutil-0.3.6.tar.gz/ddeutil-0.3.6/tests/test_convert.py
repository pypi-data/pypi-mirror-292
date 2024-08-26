import ddeutil.core.__base.convert as cc


def test_convert_str2bool():
    for _string in [
        "true",
        "True",
        "1",
        "Y",
        "y",
        "yes",
        "Yes",
    ]:
        assert cc.str2bool(_string)

    for _string in [
        "false",
        "False",
        "0",
        "N",
        "n",
        "no",
        "No",
    ]:
        assert not cc.str2bool(_string)


def test_convert_str2bool_raise():
    for _string in [
        "x",
        "X",
        "Nop",
    ]:
        try:
            cc.str2bool(_string)
        except ValueError:
            pass
