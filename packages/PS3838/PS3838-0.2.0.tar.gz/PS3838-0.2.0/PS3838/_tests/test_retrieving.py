from datetime import datetime
from unittest.mock import Mock, patch

from PS3838._PS3838Retrieve import Retrieve
from PS3838.PS3838 import retrieving

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

def test_retrieving_success():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE
    mock_api_retrieve.get_straight_line_v2.side_effect = [
        {"price": 1.5, "line_id": 1},
        {"price": 2.5, "line_id": 1},
        {"price": 3.5, "line_id": 1}
    ]

    credentials = {"username": "test", "password": "test"}
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
        }
    ]

    match_odds = retrieving(credentials, list_matches, mock_api_retrieve)

    assert len(match_odds) == 1
    assert match_odds[0][0]["id"] == 1593707406
    assert match_odds[0][1]["team1_odds"] == 1.5
    assert match_odds[0][1]["team2_odds"] == 2.5
    assert match_odds[0][1]["draw_odds"] == 3.5

@patch('PS3838.PS3838.Retrieve', autospec=True)
@patch('PS3838.PS3838.check_credentials')
@patch('PS3838.PS3838.check_list_matches')
@patch('PS3838.PS3838.retrieve_matches')
@patch('PS3838.PS3838.get_team_odds')
def test_retrieving_without_api_retrieve(mock_get_team_odds, mock_retrieve_matches, mock_check_list_matches, mock_check_credentials, mock_retrieve):
    mock_api_retrieve_instance = Mock(spec=Retrieve)
    mock_retrieve.return_value = mock_api_retrieve_instance
    mock_retrieve_matches.return_value = [
        {'id': 1593707406, 'league': 1872, 'result': 2, 'amount': 5, 'odd_min': 1.05, 'home': 'Argentina', 'away': 'Colombia', 'starts': '2024-07-15T00:00:00Z'}
    ]
    mock_get_team_odds.side_effect = [
        (1.5, 1),  # Team1 odds
        (2.5, 1),  # Draw odds
        (3.5, 1)   # Team2 odds
    ]

    credentials = {"username": "test", "password": "test"}
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
        }
    ]

    match_odds = retrieving(credentials, list_matches)

    assert len(match_odds) == 1
    assert match_odds[0][0]["id"] == 1593707406
    assert match_odds[0][1]["team1_odds"] == 1.5
    assert match_odds[0][1]["draw_odds"] == 3.5
    assert match_odds[0][1]["team2_odds"] == 2.5
    mock_retrieve.assert_called_once_with(credentials=credentials)


def test_retrieving_partial_success():
    mock_api_retrieve = Mock(spec=Retrieve)
    mock_api_retrieve.get_leagues_v3.return_value = LEAGUE_RESPONSE
    mock_api_retrieve.get_fixtures_v3.return_value = FIXTURES_RESPONSE
    mock_api_retrieve.get_straight_line_v2.side_effect = [
        {"price": 1.5, "line_id": 1},
        {"price": 2.5, "line_id": 1},
        {"price": 3.5, "line_id": 1},
        {"price": 1.8, "line_id": 2},
        {"price": 2.8, "line_id": 2},
        {"price": 3.8, "line_id": 2}
    ]

    credentials = {"username": "test", "password": "test"}
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

    match_odds = retrieving(credentials, list_matches, mock_api_retrieve)

    assert len(match_odds) == 2
    assert match_odds[0][0]["id"] == 1593707406
    assert match_odds[0][1]["team1_odds"] == 1.5
    assert match_odds[0][1]["team2_odds"] == 2.5
    assert match_odds[0][1]["draw_odds"] == 3.5
    
    assert match_odds[1][0]["id"] == 1593707403
    assert match_odds[1][1]["team1_odds"] == 1.8
    assert match_odds[1][1]["team2_odds"] == 2.8
    assert match_odds[1][1]["draw_odds"] == 3.8
    

def test_retrieving_empty_list():
    mock_api_retrieve = Mock(spec=Retrieve)

    credentials = {"username": "test", "password": "test"}
    list_matches = []

    match_odds = retrieving(credentials, list_matches, mock_api_retrieve)

    assert match_odds == []