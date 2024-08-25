import pytest

from PS3838._utils.errors import RetrieveMatchError
from PS3838._utils.tools_code import verify_result

MATCH = {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z', 'home': 'Argentina', 'away': 'Colombia', 'rotNum': '30805', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538876225}


def test_verify_result_team1_wins():
    assert verify_result(MATCH, "Argentina", "Colombia", 1) == 1

def test_verify_result_team2_wins():
    assert verify_result(MATCH, "Argentina", "Colombia", 2) == 2

def test_verify_result_draw():
    assert verify_result(MATCH, "Argentina", "Colombia", 0) == 0

def test_verify_result_team1_wins_with_result_2():
    assert verify_result(MATCH, "Colombia", "Argentina", 2) == 1

def test_verify_result_team2_wins_with_result_1():
    assert verify_result(MATCH, "Colombia", "Argentina", 1) == 2

def test_verify_result_no_result():
    assert verify_result(MATCH, "Argentina", "Colombia", None) is None

def test_verify_result_invalid_result():
    with pytest.raises(RetrieveMatchError):
        verify_result(MATCH, "Argentina", "Colombia", 3)

def test_verify_result_case_insensitive():
    assert verify_result(MATCH, "argentina", "colombia", 1) == 1

def test_verify_result_with_spaces():
    assert verify_result(MATCH, "Argen tina", "Col ombia", 1) == 1

def test_verify_result_with_punctuation():
    assert verify_result(MATCH, "Argentina!", "Colombia!", 1) == 1

def test_verify_result_partial_name():
    assert verify_result(MATCH, "Arg", "Colom", 1) == 1

def test_verify_result_mismatched_team_names():
    match =  {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z', 'home': 'Brazil', 'away': 'Chile', 'rotNum': '30805', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538876225}
    with pytest.raises(RetrieveMatchError):
        verify_result(match, "Argentina", "Colombia", 1)