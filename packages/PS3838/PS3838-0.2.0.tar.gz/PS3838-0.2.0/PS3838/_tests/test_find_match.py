from datetime import datetime

import pytest

from PS3838._utils.errors import RetrieveMatchError
from PS3838._utils.tools_code import find_match

FIXTURES = [{'id': 1593707406, 'starts': '2024-07-15T00:00:00Z', 'home': 'Argentina', 'away': 'Colombia', 'rotNum': '30805', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538876225}, {'id': 1593707403, 'starts': '2024-07-14T00:00:00Z', 'home': 'Canada', 'away': 'Uruguay', 'rotNum': '30801', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538881047}]


def test_find_match_exact_match():
    match = find_match(FIXTURES, "Argentina", "Colombia")
    assert match["id"] == 1593707406

def test_find_match_with_date():
    match_date = datetime(2024, 7, 15)
    match = find_match(FIXTURES, "Argentina", "Colombia", match_date)
    assert match["id"] == 1593707406

def test_find_match_case_insensitive():
    match = find_match(FIXTURES, "argentina", "colombia")
    assert match["id"] == 1593707406

def test_find_match_no_match():
    with pytest.raises(RetrieveMatchError):
        find_match(FIXTURES, "Chile", "Uruguay")

def test_find_match_with_similar_names():
    match = find_match(FIXTURES, "Argentin", "Colombi")
    assert match["id"] == 1593707406
    
    