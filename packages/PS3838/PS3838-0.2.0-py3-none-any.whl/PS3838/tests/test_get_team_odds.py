from unittest.mock import Mock

from PS3838._PS3838Retrieve import Retrieve
from PS3838._utils.constants import ID_SOCCER
from PS3838._utils.tools_code import get_team_odds

MATCH = {
    'id': 1593707406,
    'starts': '2024-07-15T00:00:00Z',
    'home': 'Argentina',
    'away': 'Colombia',
    'rotNum': '30805',
    'liveStatus': 2,
    'status': 'O',
    'parlayRestriction': 2,
    'altTeaser': False,
    'resultingUnit': 'Regular',
    'betAcceptanceType': 0,
    'version': 538876225,
    'league': 1872,
    'result': 1,
    'amount': 5,
    'odd_min': None
}

def test_get_team_odds_success():
    mock_api_retrieve = Mock(spec=Retrieve)
    odds_response = {
        "price": 1.5,
        "line_id": 456
    }
    mock_api_retrieve.get_straight_line_v2.return_value = odds_response

    price, line_id = get_team_odds(mock_api_retrieve, MATCH, "Argentina")
    
    assert price == 1.5
    assert line_id == 456
    mock_api_retrieve.get_straight_line_v2.assert_called_once_with(
        league_id=1872,
        handicap=0,
        odds_format="Decimal",
        sport_id=ID_SOCCER,
        event_id=1593707406,
        period_number=0,
        bet_type="MONEYLINE",
        team="Argentina"
    )

def test_get_team_odds_default_values():
    mock_api_retrieve = Mock(spec=Retrieve)
    odds_response = {}
    mock_api_retrieve.get_straight_line_v2.return_value = odds_response

    price, line_id = get_team_odds(mock_api_retrieve, MATCH, "Argentina")
    
    assert price == 0
    assert line_id == 0
    mock_api_retrieve.get_straight_line_v2.assert_called_once_with(
        league_id=1872,
        handicap=0,
        odds_format="Decimal",
        sport_id=ID_SOCCER,
        event_id=1593707406,
        period_number=0,
        bet_type="MONEYLINE",
        team="Argentina"
    )

def test_get_team_odds_with_period_number():
    mock_api_retrieve = Mock(spec=Retrieve)
    match_with_period = MATCH.copy()
    match_with_period["period_number"] = 1
    odds_response = {
        "price": 2.0,
        "line_id": 789
    }
    mock_api_retrieve.get_straight_line_v2.return_value = odds_response

    price, line_id = get_team_odds(mock_api_retrieve, match_with_period, "Argentina")
    
    assert price == 2.0
    assert line_id == 789
    mock_api_retrieve.get_straight_line_v2.assert_called_once_with(
        league_id=1872,
        handicap=0,
        odds_format="Decimal",
        sport_id=ID_SOCCER,
        event_id=1593707406,
        period_number=1,
        bet_type="MONEYLINE",
        team="Argentina"
    )