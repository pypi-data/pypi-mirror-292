from datetime import datetime
from unittest.mock import Mock

import pytest

from PS3838._PS3838Retrieve import Retrieve
from PS3838._utils.errors import RetrieveMatchError
from PS3838._utils.tools_code import retrieve_match

LEAGUE_RESPONSE = {
    "leagues": [
        {"id": 1872, "name": "CONMEBOL - Copa America"},
        {"id": 1873, "name": "La Liga"}
    ]
}

FIXTURES_RESPONSE = {
    "league": [
        {
            "events": [
                {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z', 'home': 'Argentina', 'away': 'Colombia', 'rotNum': '30805', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538876225}, {'id': 1593707403, 'starts': '2024-07-14T00:00:00Z', 'home': 'Canada', 'away': 'Uruguay', 'rotNum': '30801', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538881047}
            ]
        }
    ]
}

FIXTURES_RESPONSE_2 = {
    "league": [
        {
            "events": [
                {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z', 'home': 'Argentina', 'away': 'Colombia', 'rotNum': '30805', 'liveStatus': 2, 'status': 'C', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538876225}, {'id': 1593707403, 'starts': '2024-07-14T00:00:00Z', 'home': 'Canada', 'away': 'Uruguay', 'rotNum': '30801', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538881047}
            ]
        }
    ]
}


def test_retrieve_match_success():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE

    entry = {
        'id': 1,
        'league': 'CONMEBOL - Copa America',
        'team1': 'Colom',
        'team2': 'Argentina',
        'date': datetime(2024, 7, 15, 0, 0),
        'result': 2,
        'amount': 5,
        'odd_min': 1.05
    }

    match = retrieve_match(
        mock_api_retrieve,
        entry['league'],
        entry['team1'],
        entry['team2'],
        entry['date'],
        entry['result'],
        entry['amount'],
        entry['odd_min']
    )

    assert match["id"] == 1593707406
    assert match["league"] == 1872
    assert match["result"] == 1
    assert match["amount"] == 5
    assert match["odd_min"] == 1.05

def test_retrieve_match_no_match():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE

    entry = {
        'id': 1,
        'league': 'CONMEBOL - Copa America',
        'team1': 'Venezuela',
        'team2': 'Argentina',
        'date': datetime(2024, 7, 15, 0, 0),
        'result': 2,
        'amount': 5,
        'odd_min': 1.05
    }

    with pytest.raises(RetrieveMatchError):
        retrieve_match(
            mock_api_retrieve,
            entry['league'],
            entry['team1'],
            entry['team2'],
            entry['date'],
            entry['result'],
            entry['amount'],
            entry['odd_min']
        )

def test_retrieve_match_without_date():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE

    entry = {
        'id': 1,
        'league': 'CONMEBOL - Copa America',
        'team1': 'Colom',
        'team2': 'Argentina',
        'result': 1,
        'amount': 5,
        'odd_min': 1.05
    }

    match = retrieve_match(
        mock_api_retrieve,
        entry['league'],
        entry['team1'],
        entry['team2'],
        result = entry['result'],
        amount = entry['amount'],
        odd_min = entry['odd_min']
    )

    assert match["id"] == 1593707406
    assert match["league"] == 1872
    assert match["result"] == 2
    assert match["amount"] == 5
    assert match["odd_min"] == 1.05

def test_retrieve_match_non_existent_league():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE

    entry = {
        'id': 1,
        'league': 'Non Existent League',
        'team1': 'Colom',
        'team2': 'Argentina',
        'date': datetime(2024, 7, 15, 0, 0),
        'result': 2,
        'amount': 5,
        'odd_min': 1.05
    }

    with pytest.raises(RetrieveMatchError):
        retrieve_match(
            mock_api_retrieve,
            entry['league'],
            entry['team1'],
            entry['team2'],
            entry['date'],
            entry['result'],
            entry['amount'],
            entry['odd_min']
        )

def test_retrieve_match_non_existent_league():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE

    entry = {
        'id': 1,
        'league': 'Non Existent League',
        'team1': 'Colom',
        'team2': 'Argentina',
        'date': datetime(2024, 7, 15, 0, 0),
        'result': 2,
        'amount': 5,
        'odd_min': 1.05
    }

    with pytest.raises(RetrieveMatchError):
        retrieve_match(
            mock_api_retrieve,
            entry['league'],
            entry['team1'],
            entry['team2'],
            entry['date'],
            entry['result'],
            entry['amount'],
            entry['odd_min']
        )

def test_retrieve_match_teams_not_in_fixture():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE

    entry = {
        'id': 1,
        'league': 'CONMEBOL - Copa America',
        'team1': 'Brazil',
        'team2': 'Argentina',
        'date': datetime(2024, 7, 15, 0, 0),
        'result': 2,
        'amount': 5,
        'odd_min': 1.05
    }

    with pytest.raises(RetrieveMatchError):
        retrieve_match(
            mock_api_retrieve,
            entry['league'],
            entry['team1'],
            entry['team2'],
            entry['date'],
            entry['result'],
            entry['amount'],
            entry['odd_min']
        )

def test_retrieve_match_empty_fixtures():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = {"league": [{"events": []}]}  # Empty fixtures

    entry = {
        'id': 1,
        'league': 'CONMEBOL - Copa America',
        'team1': 'Colom',
        'team2': 'Argentina',
        'date': datetime(2024, 7, 15, 0, 0),
        'result': 2,
        'amount': 5,
        'odd_min': 1.05
    }

    with pytest.raises(RetrieveMatchError):
        retrieve_match(
            mock_api_retrieve,
            entry['league'],
            entry['team1'],
            entry['team2'],
            entry['date'],
            entry['result'],
            entry['amount'],
            entry['odd_min']
        )


def test_retrieve_match_fixture_status_other_than_O():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE_2

    entry = {
        'id': 1,
        'league': 'CONMEBOL - Copa America',
        'team1': 'Colom',
        'team2': 'Argentina',
        'date': datetime(2024, 7, 15, 0, 0),
        'result': 2,
        'amount': 5,
        'odd_min': 1.05
    }

    with pytest.raises(RetrieveMatchError):
        retrieve_match(
            mock_api_retrieve,
            entry['league'],
            entry['team1'],
            entry['team2'],
            entry['date'],
            entry['result'],
            entry['amount'],
            entry['odd_min']
        )
