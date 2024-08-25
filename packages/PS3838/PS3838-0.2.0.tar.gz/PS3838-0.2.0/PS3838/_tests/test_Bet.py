import base64
import uuid
from unittest.mock import Mock, patch

import pytest

from PS3838._PS3838Bet import Bet
from PS3838._utils.constants import URL_PS3838


@pytest.fixture
def credentials():
    return {"username": "test_user", "password": "test_pass"}

@pytest.fixture
def bet_instance(credentials):
    return Bet(credentials=credentials)

def test_get_auth_header(bet_instance, credentials):
    expected_auth_str = f"{credentials['username']}:{credentials['password']}"
    expected_b64_auth_str = base64.b64encode(expected_auth_str.encode('utf-8')).decode('utf-8')
    expected_auth_header = {"Authorization": f"Basic {expected_b64_auth_str}", "Content-Type": "application/json"}

    assert bet_instance.auth_header == expected_auth_header

@patch('requests.get')
def test_make_request_get(mock_get, bet_instance):
    mock_response = Mock()
    expected_json = {"key": "value"}
    mock_response.json.return_value = expected_json
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    endpoint = "/test"
    params = {"param": "value"}
    response = bet_instance._make_request(endpoint, params=params, method='GET')

    mock_get.assert_called_once_with(f"{URL_PS3838}{endpoint}", headers=bet_instance.auth_header, params=params)
    assert response == expected_json

@patch('requests.post')
def test_make_request_post(mock_post, bet_instance):
    mock_response = Mock()
    expected_json = {"key": "value"}
    mock_response.json.return_value = expected_json
    mock_response.raise_for_status = Mock()
    mock_post.return_value = mock_response

    endpoint = "/test"
    data = {"data": "value"}
    response = bet_instance._make_request(endpoint, data=data, method='POST')

    mock_post.assert_called_once_with(f"{URL_PS3838}{endpoint}", headers=bet_instance.auth_header, json=data)
    assert response == expected_json

@patch('PS3838.PS3838Bet.Bet._make_request')
def test_get_bets_v3(mock_make_request, bet_instance):
    expected_response = {"bets": []}
    mock_make_request.return_value = expected_response

    betlist = "test_betlist"
    from_date = "2024-01-01"
    to_date = "2024-01-02"
    bet_ids = [1, 2, 3]
    unique_request_ids = ["id1", "id2"]
    response = bet_instance.get_bets_v3(betlist, from_date, to_date, bet_ids, unique_request_ids)

    mock_make_request.assert_called_once_with(
        '/v3/bets',
        params={
            'betlist': betlist,
            'fromDate': from_date,
            'toDate': to_date,
            'betIds': '1,2,3',
            'uniqueRequestIds': 'id1,id2'
        }
    )
    assert response == expected_response

@patch('PS3838.PS3838Bet.Bet._make_request')
def test_place_bet(mock_make_request, bet_instance):
    expected_response = {
        "status": "ACCEPTED",
        "straightBet": {
            "betId": 759629245,
            "wagerNumber": 1,
            "betStatus": "ACCEPTED"
        }
    }
    mock_make_request.return_value = expected_response

    odds_format = "Decimal"
    stake = 5.0
    line_id = 12345
    sport_id = 29
    event_id = 98765
    period_number = 0
    bet_type = "MONEYLINE"
    team = "Team1"
    response = bet_instance.place_bet(odds_format, stake, line_id, sport_id, event_id, period_number, bet_type, team)

    data = {
        "oddsFormat": odds_format,
        "uniqueRequestId": str(uuid.uuid4()),  # This needs to be dynamically generated, so we can't assert it directly
        "acceptBetterLine": True,
        "stake": stake,
        "winRiskStake": "RISK",
        "lineId": line_id,
        "altLineId": None,
        "pitcher1MustStart": True,
        "pitcher2MustStart": True,
        "fillType": "NORMAL",
        "sportId": sport_id,
        "eventId": event_id,
        "periodNumber": period_number,
        "betType": bet_type,
        "team": team,
        "side": None,
        "handicap": None
    }

    mock_make_request.assert_called_once()
    called_args, called_kwargs = mock_make_request.call_args
    assert called_args == ('/v2/bets/place',)
    assert called_kwargs['data'].keys() == data.keys()  # We check the keys instead of values because uniqueRequestId is dynamic
    assert called_kwargs['method'] == 'POST'

    assert response == expected_response

@patch('PS3838.PS3838Bet.Bet._make_request')
def test_check_maintenance(mock_make_request, bet_instance):
    expected_response = {"status": "ALL_BETTING_ENABLED"}
    mock_make_request.return_value = expected_response

    response = bet_instance.check_maintenance()

    mock_make_request.assert_called_once_with('/v1/bets/betting-status')
    assert response == expected_response