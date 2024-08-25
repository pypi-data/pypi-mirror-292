from datetime import datetime

import pytest

from PS3838._utils.errors import ParameterError
from PS3838._utils.tools_check import check_list_matches


def test_check_list_matches_success():
    list_matches = [
        {
            "league": "Premier League",
            "team1": "Team A",
            "team2": "Team B",
            "date": datetime(2024, 7, 15, 0, 0)
        },
        {
            "league": "La Liga",
            "team1": "Team C",
            "team2": "Team D",
            "date": datetime(2024, 7, 16, 0, 0)
        }
    ]
    try:
        check_list_matches(list_matches)
    except ParameterError:
        pytest.fail("check_list_matches raised ParameterError unexpectedly!")

def test_check_list_matches_missing():
    with pytest.raises(ParameterError, match="The list of matches is missing"):
        check_list_matches(None)

def test_check_list_matches_not_a_list():
    with pytest.raises(ParameterError, match="The list of matches must be a list"):
        check_list_matches("not_a_list")

def test_check_list_matches_invalid_match():
    list_matches = [
        {
            "league": "Premier League",
            "team1": "Team A",
            "team2": "Team B",
            "date": datetime(2024, 7, 15, 0, 0)
        },
        {
            "league": "La Liga",
            "team1": "Team C"
            # Missing team2 and date
        }
    ]
    with pytest.raises(ParameterError):
        check_list_matches(list_matches)

