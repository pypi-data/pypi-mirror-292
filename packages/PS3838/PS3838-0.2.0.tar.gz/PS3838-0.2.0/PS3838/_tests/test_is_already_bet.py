from unittest.mock import patch

from PS3838._utils.tools_code import is_already_bet


@patch('PS3838.utils.tools_code.Bet')
def test_is_already_bet_true(mock_api_bet):
    match = {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z'}
    
    mock_api_bet.get_bets_v3.return_value = {
        "straightBets": [
            {"eventId": 1593707406, "betStatus": "ACCEPTED"}
        ]
    }
    
    assert is_already_bet(mock_api_bet, match) == True

@patch('PS3838.utils.tools_code.Bet')
def test_is_already_bet_false_no_bets(mock_api_bet):
    match = {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z'}
    
    mock_api_bet.get_bets_v3.return_value = {}
    
    assert is_already_bet(mock_api_bet, match) == False
    
@patch('PS3838.utils.tools_code.Bet')
def test_is_already_bet_false_different_event_id(mock_api_bet):
    match = {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z'}
    
    mock_api_bet.get_bets_v3.return_value = {
        "straightBets": [
            {"eventId": 1234567890, "betStatus": "ACCEPTED"}
        ]
    }
    
    assert is_already_bet(mock_api_bet, match) == False

@patch('PS3838.utils.tools_code.Bet')
def test_is_already_bet_false_different_bet_status(mock_api_bet):
    match = {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z'}
    
    mock_api_bet.get_bets_v3.return_value = {
        "straightBets": [
            {"eventId": 1593707406, "betStatus": "PENDING"}
        ]
    }
    
    assert is_already_bet(mock_api_bet, match) == False

@patch('PS3838.utils.tools_code.Bet')
def test_is_already_bet_no_straight_bets_key(mock_api_bet):
    match = {'id': 1593707406, 'starts': '2024-07-15T00:00:00Z'}
    
    mock_api_bet.get_bets_v3.return_value = {}
    
    assert is_already_bet(mock_api_bet, match) == False
