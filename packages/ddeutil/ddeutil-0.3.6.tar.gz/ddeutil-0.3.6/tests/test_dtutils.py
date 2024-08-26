import datetime

import ddeutil.core.dtutils as dtutils


def test_get_date():
    assert datetime.datetime.now(
        tz=dtutils.LOCAL_TZ
    ).date() == dtutils.get_date("date")


def test_replace_date():
    assert datetime.datetime(2023, 1, 31, 0, 0) == dtutils.replace_date(
        datetime.datetime(2023, 1, 31, 13, 2, 47),
        mode="day",
    )

    assert datetime.datetime(2023, 1, 1, 0, 0) == dtutils.replace_date(
        datetime.datetime(2023, 1, 31, 13, 2, 47),
        mode="year",
    )
