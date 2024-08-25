from datetime import datetime
from unittest.mock import patch

import pytest

from PS3838 import betting
from PS3838._utils.constants import ID_SOCCER
from PS3838._utils.errors import CredentialError, ParameterError

CREDENTIALS = {"username": "test", "password": "test"}
LIST_MATCHES = [
    {'league': 'CONMEBOL - Copa America', 'team1': 'Colom', 'team2': 'Argentina', 'date': datetime(2024, 7, 15, 0, 0), 'result': 1, 'amount': 5, 'odd_min': 1.05},
    {'league': 'CONMEBOL - Copa America', 'team1': 'Canada', 'team2': 'Uruguay', 'date': datetime(2024, 7, 14, 0, 0), 'result': 2, 'amount': 10, 'odd_min': 1.10}
]
RETRIEVING_RESPONSE = [
    (
        {'id': 1593707406, 'league': 1872, 'result': 1, 'amount': 5, 'odd_min': 1.05, 'home': 'Argentina', 'away': 'Colombia', 'starts': '2024-07-15T00:00:00Z', 'line_id': 1},
        {'team1_odds': 2.17, 'draw_odds': 2.94, 'team2_odds': 4.41}
    ),
    (
        {'id': 1593707403, 'league': 1872, 'result': 2, 'amount': 10, 'odd_min': 1.10, 'home': 'Canada', 'away': 'Uruguay', 'starts': '2024-07-14T00:00:00Z', 'line_id': 2},
        {'team1_odds': 2.50, 'draw_odds': 3.20, 'team2_odds': 2.70}
    )
]

@patch('PS3838.PS3838.check_list_matches')
@patch('PS3838.PS3838.check_credentials')
@patch('PS3838.PS3838.retrieving')
@patch('PS3838.PS3838.Bet', autospec=True)
def test_betting_maintenance(mock_bet, mock_retrieving, mock_check_credentials, mock_check_list_matches):
    mock_bet_instance = mock_bet.return_value
    mock_retrieving.return_value = []
    
    mock_bet_instance.check_maintenance.return_value = {"status": "ALL_BETTING_CLOSED"}
    
    credentials = CREDENTIALS
    list_matches = LIST_MATCHES

    assert None == betting(credentials, list_matches)
    mock_check_credentials.assert_called_once_with(credentials)
    mock_check_list_matches.assert_called_once_with(list_matches, to_bet=True)
    mock_bet_instance.check_maintenance.assert_called_once()
    mock_bet_instance.place_bet.assert_not_called()
    mock_retrieving.assert_not_called()
    

@patch('PS3838.PS3838.check_credentials')
def test_betting_invalid_credentials(mock_check_credentials):
    mock_check_credentials.side_effect = CredentialError("Problem with the credentials")

    credentials = {"username": ""}
    list_matches = LIST_MATCHES
    
    with pytest.raises(CredentialError):
        betting(credentials, list_matches)

@patch('PS3838.utils.tools_check.check_list_matches')
def test_betting_invalid_matches(mock_check_list_matches):
    mock_check_list_matches.side_effect = ParameterError("Problem with the list of matches")

    credentials = CREDENTIALS
    list_matches = []
    
    with pytest.raises(ParameterError):
        betting(credentials, list_matches)


@patch('PS3838.PS3838.verify_odds')
@patch('PS3838.PS3838.is_already_bet')
@patch('PS3838.PS3838.check_list_matches')
@patch('PS3838.PS3838.check_credentials')
@patch('PS3838.PS3838.Retrieve', autospec=True)
@patch('PS3838.PS3838.Bet', autospec=True)
@patch('PS3838.PS3838.retrieving')
def test_betting_success(mock_retrieving, mock_bet, mock_retrieve, mock_check_credentials, mock_check_list_matches, mock_is_already_bet, mock_verify_odds):
    mock_bet_instance = mock_bet.return_value
    mock_retrieve_instance = mock_retrieve.return_value

    # Mock the check_maintenance method and the place_bet method
    mock_is_already_bet.return_value = False
    mock_verify_odds.return_value = True
    mock_bet_instance.check_maintenance.return_value = {"status": "ALL_BETTING_ENABLED"}
    mock_bet_instance.place_bet.return_value = {
    "status": "ACCEPTED",
    "errorCode": "ALL_BETTING_CLOSED",
    "betId": 0,
    "uniqueRequestId": "A9EB2EB1-13A5-4600-9F1B-4859379CDEC4",
    "betterLineWasAccepted": True,
    "price": 0
}

    # Mock the retrieving function
    mock_retrieving.return_value = RETRIEVING_RESPONSE
    
    credentials = CREDENTIALS
    list_matches = LIST_MATCHES
    
    betting(credentials, list_matches)
    
    mock_check_credentials.assert_called_once_with(credentials)
    mock_check_list_matches.assert_called_once_with(list_matches, to_bet=True)
    mock_bet.assert_called_once_with(credentials=credentials)
    mock_retrieve.assert_called_once_with(credentials=credentials)
    mock_bet_instance.check_maintenance.assert_called_once()
    mock_retrieving.assert_called_once_with(credentials, list_matches, mock_retrieve_instance)
    
    mock_bet_instance.place_bet.assert_any_call(
        odds_format="Decimal", stake=5, line_id=1, sport_id=ID_SOCCER, event_id=1593707406, period_number=0, bet_type="MONEYLINE", team="TEAM1"
    )
    mock_bet_instance.place_bet.assert_any_call(
        odds_format="Decimal", stake=10, line_id=2, sport_id=ID_SOCCER, event_id=1593707403, period_number=0, bet_type="MONEYLINE", team="TEAM2"
    )

@patch('PS3838.PS3838.verify_odds')
@patch('PS3838.PS3838.is_already_bet')
@patch('PS3838.PS3838.check_list_matches')
@patch('PS3838.PS3838.check_credentials')
@patch('PS3838.PS3838.Retrieve', autospec=True)
@patch('PS3838.PS3838.Bet', autospec=True)
@patch('PS3838.PS3838.retrieving')
def test_betting_exception_handling(mock_retrieving, mock_bet, mock_retrieve, mock_check_credentials, mock_check_list_matches, mock_is_already_bet, mock_verify_odds):
    mock_bet_instance = mock_bet.return_value
    mock_retrieve_instance = mock_retrieve.return_value
    mock_check_credentials.return_value = None
    mock_check_list_matches.return_value = None

    # Mock the check_maintenance method
    mock_bet_instance.check_maintenance.return_value = {"status": "ALL_BETTING_ENABLED"}
    mock_is_already_bet.return_value = False
    mock_verify_odds.return_value = True

    # Mock the retrieving function
    mock_retrieving.return_value = [
        (
            {'id': 1593707406, 'league': 1872, 'result': 1, 'amount': 5, 'odd_min': 1.05, 'home': 'Argentina', 'away': 'Colombia', 'starts': '2024-07-15T00:00:00Z', 'line_id': 1},
            {'team1_odds': 2.17, 'draw_odds': 2.94, 'team2_odds': 4.41}
        )
    ]
    
    # Mock the place_bet method to raise an exception
    mock_bet_instance.place_bet.side_effect = Exception("Test exception")

    credentials = {"username": "test", "password": "test"}
    list_matches = [
        {'id': 1, 'league': 'CONMEBOL - Copa America', 'team1': 'Colom', 'team2': 'Argentina', 'date': datetime(2024, 7, 15, 0, 0), 'result': 1, 'amount': 5, 'odd_min': 1.05}
    ]
    
    betting(credentials, list_matches, logger_active=True)
    
    mock_check_credentials.assert_called_once_with(credentials)
    mock_check_list_matches.assert_called_once_with(list_matches, to_bet=True)
    mock_bet.assert_called_once_with(credentials=credentials)
    mock_retrieve.assert_called_once_with(credentials=credentials)
    mock_bet_instance.check_maintenance.assert_called_once()
    mock_retrieving.assert_called_once_with(credentials, list_matches, mock_retrieve_instance)
    
    mock_bet_instance.place_bet.assert_called_once_with(
        odds_format="Decimal", stake=5, line_id=1, sport_id=ID_SOCCER, event_id=1593707406, period_number=0, bet_type="MONEYLINE", team="TEAM1"
    )
    # Ensure the exception is handled, and further calls are not made

@patch('PS3838.PS3838.is_already_bet')
@patch('PS3838.PS3838.check_list_matches')
@patch('PS3838.PS3838.check_credentials')
@patch('PS3838.PS3838.Retrieve', autospec=True)
@patch('PS3838.PS3838.Bet', autospec=True)
@patch('PS3838.PS3838.retrieving')
def test_betting_with_already_bet(mock_retrieving, mock_bet, mock_retrieve, mock_check_credentials, mock_check_list_matches, mock_is_already_bet):
    mock_bet_instance = mock_bet.return_value
    mock_retrieve_instance = mock_retrieve.return_value

    # Mock the check_maintenance method and the place_bet method
    mock_is_already_bet.return_value = True
    mock_bet_instance.check_maintenance.return_value = {"status": "ALL_BETTING_ENABLED"}

    # Mock the retrieving function
    mock_retrieving.return_value = RETRIEVING_RESPONSE
    
    credentials = CREDENTIALS
    list_matches = LIST_MATCHES
    
    betting(credentials, list_matches)
    
    mock_check_credentials.assert_called_once_with(credentials)
    mock_check_list_matches.assert_called_once_with(list_matches, to_bet=True)
    mock_bet.assert_called_once_with(credentials=credentials)
    mock_retrieve.assert_called_once_with(credentials=credentials)
    mock_bet_instance.check_maintenance.assert_called_once()
    mock_retrieving.assert_called_once_with(credentials, list_matches, mock_retrieve_instance)
    
    mock_bet_instance.place_bet.assert_not_called()

@patch('PS3838.PS3838.verify_odds')
@patch('PS3838.PS3838.is_already_bet')
@patch('PS3838.PS3838.check_list_matches')
@patch('PS3838.PS3838.check_credentials')
@patch('PS3838.PS3838.Retrieve', autospec=True)
@patch('PS3838.PS3838.Bet', autospec=True)
@patch('PS3838.PS3838.retrieving')
def test_betting_without_verify_odds(mock_retrieving, mock_bet, mock_retrieve, mock_check_credentials, mock_check_list_matches, mock_is_already_bet, mock_verify_odds):
    mock_bet_instance = mock_bet.return_value
    mock_retrieve_instance = mock_retrieve.return_value
    mock_check_list_matches.return_value = None
    mock_check_credentials.return_value = None

    # Mock the check_maintenance method and the place_bet method
    mock_is_already_bet.return_value = False
    mock_verify_odds.return_value = False
    mock_bet_instance.check_maintenance.return_value = {"status": "ALL_BETTING_ENABLED"}

    # Mock the retrieving function
    mock_retrieving.return_value = RETRIEVING_RESPONSE
    
    credentials = CREDENTIALS
    list_matches = LIST_MATCHES
    
    betting(credentials, list_matches)
    
    mock_check_credentials.assert_called_once_with(credentials)
    mock_check_list_matches.assert_called_once_with(list_matches, to_bet=True)
    mock_bet.assert_called_once_with(credentials=credentials)
    mock_retrieve.assert_called_once_with(credentials=credentials)
    mock_bet_instance.check_maintenance.assert_called_once()
    mock_retrieving.assert_called_once_with(credentials, list_matches, mock_retrieve_instance)
    
    mock_bet_instance.place_bet.assert_not_called()