import base64
from unittest.mock import Mock, patch

import pytest
import requests

from PS3838._PS3838Retrieve import Retrieve
from PS3838._utils.constants import URL_PS3838


@pytest.fixture
def credentials():
    return {"username": "test_user", "password": "test_pass"}

@pytest.fixture
def retrieve_instance(credentials):
    return Retrieve(credentials=credentials)

def test_get_auth_header(retrieve_instance, credentials):
    expected_auth_str = f"{credentials['username']}:{credentials['password']}"
    expected_b64_auth_str = base64.b64encode(expected_auth_str.encode('utf-8')).decode('utf-8')
    expected_auth_header = {"Authorization": f"Basic {expected_b64_auth_str}"}

    assert retrieve_instance._auth_header == expected_auth_header

@patch('requests.get')
def test_make_request_get(mock_get, retrieve_instance):
    mock_response = Mock()
    expected_json = {"key": "value"}
    mock_response.json.return_value = expected_json
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    endpoint = "/test"
    params = {"param": "value"}
    response = retrieve_instance._make_request(endpoint, params=params)

    mock_get.assert_called_once_with(f"{URL_PS3838}{endpoint}", headers=retrieve_instance._auth_header, params=params)
    assert response == expected_json

@patch('requests.get')
def test_make_request_get_error(mock_get, retrieve_instance):
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP error")
    mock_get.return_value = mock_response

    endpoint = "/test"
    params = {"param": "value"}
    response = retrieve_instance._make_request(endpoint, params=params)

    mock_get.assert_called_once_with(f"{URL_PS3838}{endpoint}", headers=retrieve_instance._auth_header, params=params)
    assert response == {}

@patch('PS3838.PS3838Retrieve.Retrieve._make_request')
def test_get_fixtures_v3(mock_make_request, retrieve_instance):
    expected_response = {"fixtures": []}
    mock_make_request.return_value = expected_response

    sport_id = 29
    league_ids = [123, 456]
    is_live = True
    since = 1609459200
    event_ids = [789, 101]
    response = retrieve_instance.get_fixtures_v3(sport_id, league_ids, is_live, since, event_ids)

    expected_params = {
        "sportId": sport_id,
        "leagueIds": "123,456",
        "isLive": 1,
        "since": since,
        "eventIds": "789,101"
    }

    mock_make_request.assert_called_once_with("/v3/fixtures", expected_params)
    assert response == expected_response

@patch('PS3838.PS3838Retrieve.Retrieve._make_request')
def test_get_straight_line_v2(mock_make_request, retrieve_instance):
    expected_response = {"line": []}
    mock_make_request.return_value = expected_response

    league_id = 123
    handicap = -1.5
    odds_format = "Decimal"
    sport_id = 29
    event_id = 98765
    period_number = 1
    bet_type = "MONEYLINE"
    team = "Team1"
    side = "OVER"
    response = retrieve_instance.get_straight_line_v2(league_id, handicap, odds_format, sport_id, event_id, period_number, bet_type, team, side)

    expected_params = {
        "leagueId": league_id,
        "handicap": handicap,
        "oddsFormat": odds_format,
        "sportId": sport_id,
        "eventId": event_id,
        "periodNumber": period_number,
        "betType": bet_type,
        "team": team,
        "side": side
    }

    mock_make_request.assert_called_once_with("/v2/line", expected_params)
    assert response == expected_response

@patch('PS3838.PS3838Retrieve.Retrieve._make_request')
def test_get_sports_v3(mock_make_request, retrieve_instance):
    expected_response = {"sports": []}
    mock_make_request.return_value = expected_response

    response = retrieve_instance.get_sports_v3()

    mock_make_request.assert_called_once_with("/v3/sports")
    assert response == expected_response

@patch('PS3838.PS3838Retrieve.Retrieve._make_request')
def test_get_leagues_v3(mock_make_request, retrieve_instance):
    expected_response = {"leagues": []}
    mock_make_request.return_value = expected_response

    sport_id = 29
    response = retrieve_instance.get_leagues_v3(sport_id)

    expected_params = {"sportId": sport_id}

    mock_make_request.assert_called_once_with("/v3/leagues", expected_params)
    assert response == expected_response


