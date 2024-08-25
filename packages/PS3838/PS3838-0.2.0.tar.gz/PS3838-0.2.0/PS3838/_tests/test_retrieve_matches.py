from datetime import datetime
from unittest.mock import Mock

from PS3838._PS3838Retrieve import Retrieve
from PS3838._utils.tools_code import retrieve_matches

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
                {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z', 'home': 'Argentina', 'away': 'Colombia', 'rotNum': '30805', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538876225},
                {'id': 1593707403, 'starts': '2024-07-14T00:00:00Z', 'home': 'Canada', 'away': 'Uruguay', 'rotNum': '30801', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 538881047}
            ]
        }
    ]
}


def test_retrieve_matches_success():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE

    list_matches = [
        {
            'id': 1,
            'league': 'CONMEBOL - Copa America',
            'team1': 'Colom',
            'team2': 'Argentina',
            'date': datetime(2024, 7, 15, 0, 0),
            'result': 2,
            'amount': 5,
            'odd_min': 1.05
        },
        {
            'id': 2,
            'league': 'CONMEBOL - Copa America',
            'team1': 'Canada',
            'team2': 'Uruguay',
            'date': datetime(2024, 7, 14, 0, 0),
            'result': 1,
            'amount': 10,
            'odd_min': 1.10
        }
    ]

    matches = retrieve_matches(list_matches, mock_api_retrieve)

    assert len(matches) == 2
    assert matches[0]["id"] == 1593707406
    assert matches[0]["league"] == 1872
    assert matches[0]["result"] == 1
    assert matches[0]["amount"] == 5
    assert matches[0]["odd_min"] == 1.05
    assert matches[1]["id"] == 1593707403
    assert matches[1]["league"] == 1872
    assert matches[1]["result"] == 1
    assert matches[1]["amount"] == 10
    assert matches[1]["odd_min"] == 1.10

def test_retrieve_matches_partial_success():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE

    list_matches = [
        {
            'id': 1,
            'league': 'CONMEBOL - Copa America',
            'team1': 'Colom',
            'team2': 'Argentina',
            'date': datetime(2024, 7, 15, 0, 0),
            'result': 2,
            'amount': 5,
            'odd_min': 1.05
        },
        {
            'id': 2,
            'league': 'CONMEBOL - Copa America',
            'team1': 'NonExistent',
            'team2': 'Uruguay',
            'date': datetime(2024, 7, 14, 0, 0),
            'result': 1,
            'amount': 10,
            'odd_min': 1.10
        }
    ]

    matches = retrieve_matches(list_matches, mock_api_retrieve)

    assert len(matches) == 1
    assert matches[0]["id"] == 1593707406
    assert matches[0]["league"] == 1872
    assert matches[0]["result"] == 1
    assert matches[0]["amount"] == 5
    assert matches[0]["odd_min"] == 1.05


def test_retrieve_matches_empty_list():
    mock_api_retrieve = Mock(spec=Retrieve)
    list_matches = []

    matches = retrieve_matches(list_matches, mock_api_retrieve)

    assert matches == []

def test_retrieve_matches_no_date():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE

    list_matches = [
        {
            'id': 1,
            'league': 'CONMEBOL - Copa America',
            'team1': 'Colom',
            'team2': 'Argentina',
            'result': 2,
            'amount': 5,
            'odd_min': 1.05
        },
        {
            'id': 2,
            'league': 'CONMEBOL - Copa America',
            'team1': 'Canada',
            'team2': 'Uruguay',
            'result': 1,
            'amount': 10,
            'odd_min': 1.10
        }
    ]

    matches = retrieve_matches(list_matches, mock_api_retrieve)

    assert len(matches) == 2
    assert matches[0]["id"] == 1593707406
    assert matches[0]["league"] == 1872
    assert matches[0]["result"] == 1
    assert matches[0]["amount"] == 5
    assert matches[0]["odd_min"] == 1.05
    assert matches[1]["id"] == 1593707403
    assert matches[1]["league"] == 1872
    assert matches[1]["result"] == 1
    assert matches[1]["amount"] == 10
    assert matches[1]["odd_min"] == 1.10