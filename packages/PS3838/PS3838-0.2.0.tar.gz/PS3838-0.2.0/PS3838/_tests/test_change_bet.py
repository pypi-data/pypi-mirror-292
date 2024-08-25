
from PS3838._utils.tools_code import change_date


def test_change_date_add_days():
    date = "2024-07-15T00:00:00Z"
    expected_date = "2024-07-17T00:00:00Z"
    assert change_date(date, 2, 0) == expected_date

def test_change_date_add_hours():
    date = "2024-07-15T00:00:00Z"
    expected_date = "2024-07-15T05:00:00Z"
    assert change_date(date, 0, 5) == expected_date

def test_change_date_add_days_and_hours():
    date = "2024-07-15T00:00:00Z"
    expected_date = "2024-07-17T05:00:00Z"
    assert change_date(date, 2, 5) == expected_date

def test_change_date_subtract_days():
    date = "2024-07-15T00:00:00Z"
    expected_date = "2024-07-13T00:00:00Z"
    assert change_date(date, -2, 0) == expected_date

def test_change_date_subtract_hours():
    date = "2024-07-15T05:00:00Z"
    expected_date = "2024-07-15T00:00:00Z"
    assert change_date(date, 0, -5) == expected_date

def test_change_date_subtract_days_and_hours():
    date = "2024-07-15T05:00:00Z"
    expected_date = "2024-07-13T00:00:00Z"
    assert change_date(date, -2, -5) == expected_date

def test_change_date_add_days_over_month():
    date = "2024-07-28T00:00:00Z"
    expected_date = "2024-08-02T00:00:00Z"
    assert change_date(date, 5, 0) == expected_date

def test_change_date_add_hours_over_day():
    date = "2024-07-15T23:00:00Z"
    expected_date = "2024-07-16T01:00:00Z"
    assert change_date(date, 0, 2) == expected_date
