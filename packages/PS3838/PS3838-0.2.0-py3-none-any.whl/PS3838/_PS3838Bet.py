import base64
import uuid
from typing import Any, Dict, List, Optional

import requests

from PS3838._utils.constants import URL_PS3838


class Bet():
    """
    This class is used to place bets on the PS3838 API.
    """
    def __init__(
        self, 
        credentials: Dict[str, str],
        *args,
        **kwargs
    ):
        self.credentials = credentials
        self.base_url = URL_PS3838
        self.auth_header = self._get_auth_header()

    def _get_auth_header(self) -> Dict[str, str]:
        auth_str = f"{self.credentials['username']}:{self.credentials['password']}"
        b64_auth_str = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        return {"Authorization": f"Basic {b64_auth_str}", "Content-Type": "application/json"}
    
    def _make_request(
        self, 
        endpoint: str, 
        data: Dict[str, Any] = None, 
        params: Dict[str, Any] = None, 
        method: str = 'GET'
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=self.auth_header, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.auth_header, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()  # Try to parse JSON response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except requests.exceptions.JSONDecodeError as json_err:
            print(f"JSON decode error occurred: {json_err}")
            print(f"Response content: {response.text}")
        
        return {}

    def get_bets_v3(
        self, 
        betlist: Optional[str] = None, 
        from_date: Optional[str] = None, 
        to_date: Optional[str] = None,
        bet_ids: List[int] = None, 
        unique_request_ids: List[str] = None
    ) -> Dict[str, Any]:
        '''
        Get a list of bets that are already placed

        parameters:
            betlist: 'ALL' or 'SETTLED' or 'PENDING' or 'CANCELLED' or 'ALL_PENDING' (Optional)
            from_date: ISO8601 format (REQUIRED when betlist is provided)
            to_date: ISO8601 format (REQUIRED when betlist is provided)
            bet_ids: list of bet IDs
            unique_request_ids: list of unique request IDs
        
        return:
            JSON response
        '''

        params = {
            'betlist': betlist,
            'fromDate': from_date,
            'toDate': to_date,
            'betIds': ','.join(map(str, bet_ids)) if bet_ids else None,
            'uniqueRequestIds': ','.join(unique_request_ids) if unique_request_ids else None
        }
        return self._make_request('/v3/bets', params=params)

    def place_bet(
        self, 
        stake: float, 
        line_id: int, 
        sport_id: int, 
        event_id: int, 
        period_number: int, 
        team: str, 
        side: str = None, 
        handicap: float = None
    ) -> Dict[str, Any]:
        """
        Place a bet on the PS3838 API.
        
        Parameters:
            stake: The amount of the bet (min 5 euros)
            line_id: The line ID of the bet
            sport_id: The sport ID of the event (football = 29)
            event_id: The event ID of the event
            period_number: The period number of the event (0 for full time)
            team: The team to bet on "TEAM1" or "TEAM2" or "DRAW"
            side: The side to bet on (optional)
            handicap: The handicap value (optional)
            Other values that will be passed to the API are hardcoded
            
        Returns:
            The response from the API
        """

        # Generate a unique request ID
        unique_request_id = str(uuid.uuid4())  
        
        # Construct the data payload
        data = {
            "oddsFormat": "DECIMAL",
            "uniqueRequestId": unique_request_id,
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
            "betType": "MONEYLINE",
            "team": team,
            "side": side,
            "handicap": handicap
        }

        return self._make_request('/v2/bets/place', data=data, method='POST')

    def check_maintenance(self) -> Dict[str, Any]:
        """
        Check the maintenance status of the PS3838 API. If the status is 'ALL_BETTING_ENABLED', then betting is allowed.
        Else, it means that the API is in maintenance mode and betting is disabled.
        """
        return self._make_request('/v1/bets/betting-status')
