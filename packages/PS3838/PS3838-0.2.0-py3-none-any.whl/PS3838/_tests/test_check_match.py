from datetime import datetime

import pytest

from PS3838._utils.errors import ParameterError
from PS3838._utils.tools_check import check_match


def test_check_match_success():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "date": datetime(2024, 7, 15, 0, 0)
    }
    try:
        check_match(match)
    except ParameterError:
        pytest.fail("check_match raised ParameterError unexpectedly!")

def test_check_match_success_to_bet():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "date": datetime(2024, 7, 15, 0, 0),
        "result": 1,
        "amount": 10,
        "odd_min": 1.5
    }
    try:
        check_match(match, to_bet=True)
    except ParameterError:
        pytest.fail("check_match raised ParameterError unexpectedly!")

def test_check_match_not_a_dict():
    with pytest.raises(ParameterError, match="Each match must be a dictionary"):
        check_match("not_a_dict")

def test_check_match_missing_league():
    match = {
        "team1": "Team A",
        "team2": "Team B"
    }
    with pytest.raises(ParameterError):
        check_match(match)

def test_check_match_missing_team1():
    match = {
        "league": "Premier League",
        "team2": "Team B"
    }
    with pytest.raises(ParameterError):
        check_match(match)

def test_check_match_missing_team2():
    match = {
        "league": "Premier League",
        "team1": "Team A"
    }
    with pytest.raises(ParameterError):
        check_match(match)

def test_check_match_league_not_str_or_int():
    match = {
        "league": ["Premier League"],
        "team1": "Team A",
        "team2": "Team B"
    }
    with pytest.raises(ParameterError):
        check_match(match)

def test_check_match_team1_not_str():
    match = {
        "league": "Premier League",
        "team1": 123,
        "team2": "Team B"
    }
    with pytest.raises(ParameterError):
        check_match(match)

def test_check_match_team2_not_str():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": 123
    }
    with pytest.raises(ParameterError):
        check_match(match)

def test_check_match_date_not_datetime():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "date": "2024-07-15"
    }
    with pytest.raises(ParameterError):
        check_match(match)

def test_check_match_missing_result_to_bet():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "amount": 10,
        "odd_min": 1.5
    }
    with pytest.raises(ParameterError):
        check_match(match, to_bet=True)

def test_check_match_missing_amount_to_bet():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "result": 1,
        "odd_min": 1.5
    }
    with pytest.raises(ParameterError):
        check_match(match, to_bet=True)

def test_check_match_missing_odd_min_to_bet():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "result": 1,
        "amount": 10
    }
    with pytest.raises(ParameterError):
        check_match(match, to_bet=True)

def test_check_match_result_not_int():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "result": "one",
        "amount": 10,
        "odd_min": 1.5
    }
    with pytest.raises(ParameterError):
        check_match(match, to_bet=True)

def test_check_match_amount_not_int():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "result": 1,
        "amount": "ten",
        "odd_min": 1.5
    }
    with pytest.raises(ParameterError):
        check_match(match, to_bet=True)

def test_check_match_odd_min_not_float():
    match = {
        "league": "Premier League",
        "team1": "Team A",
        "team2": "Team B",
        "result": 1,
        "amount": 10,
        "odd_min": 1
    }
    with pytest.raises(ParameterError):
        check_match(match, to_bet=True)

