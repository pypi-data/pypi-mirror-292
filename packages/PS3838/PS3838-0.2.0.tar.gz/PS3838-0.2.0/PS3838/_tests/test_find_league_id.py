import pytest

from PS3838._utils.errors import RetrieveMatchError
from PS3838._utils.tools_code import find_league_id

LEAGUES = {
        "leagues": [
            {'id': 199618, 'name': 'Italy - Super Cup Bookings', 'homeTeamType': 'Team1', 'hasOfferings': False, 'container': 'Italy', 'allowRoundRobins': True, 'leagueSpecialsCount': 0, 'eventSpecialsCount': 0, 'eventCount': 0}, {'id': 1979, 'name': 'England - FA Cup', 'homeTeamType': 'Team1', 'hasOfferings': False, 'container': 'England', 'allowRoundRobins': True, 'leagueSpecialsCount': 0, 'eventSpecialsCount': 0, 'eventCount': 0}, {'id': 1989, 'name': 'Estonia - Meistriliiga', 'homeTeamType': 'Team1', 'hasOfferings': True, 'container': 'Estonia', 'allowRoundRobins': True, 'leagueSpecialsCount': 0, 'eventSpecialsCount': 20, 'eventCount': 3}, {'id': 196861, 'name': 'Norway - Toppserien Women', 'homeTeamType': 'Team1', 'hasOfferings': False, 'container': 'Norway', 'allowRoundRobins': True, 'leagueSpecialsCount': 0, 'eventSpecialsCount': 0, 'eventCount': 0}, {'id': 218098, 'name': 'Israel - Liga Leumit U19', 'homeTeamType': 'Team1', 'hasOfferings': False, 'container': 'Israel', 'allowRoundRobins': False, 'leagueSpecialsCount': 0, 'eventSpecialsCount': 0, 'eventCount': 0}
        ]
    }

def test_find_league_id_by_id():
    assert find_league_id(LEAGUES, 1989) == 1989

def test_find_league_id_by_name():
    assert find_league_id(LEAGUES, "England - FA Cup") == 1979

def test_find_league_id_case_insensitive():
    assert find_league_id(LEAGUES, "england fa cup") == 1979

def test_find_league_id_with_spaces():
    assert find_league_id(LEAGUES, " england -fa cup  ") == 1979

def test_find_league_id_with_punctuation():
    assert find_league_id(LEAGUES, " england! -fa @cup  ") == 1979

def test_find_league_id_not_found():
    with pytest.raises(RetrieveMatchError):
        find_league_id(LEAGUES, "Bundesliga")

def test_find_league_id_invalid_type():
    with pytest.raises(RetrieveMatchError):
        find_league_id(LEAGUES, ["La Liga"])