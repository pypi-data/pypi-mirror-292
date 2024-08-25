import base64
from typing import Any, Dict, List, Optional

import requests

from PS3838._utils.constants import URL_PS3838


class Retrieve():
    def __init__(
        self,
        credentials : Dict[str, str], 
        *args,
        **kwargs,
    ):
        self._credentials = credentials
        self._base_url = URL_PS3838
        self._auth_header = self._get_auth_header()

    def _get_auth_header(self) -> Dict[str, str]:
        auth_str = f"{self._credentials['username']}:{self._credentials['password']}"
        b64_auth_str = base64.b64encode(auth_str.encode('utf-8')).decode('utf-8')
        return {"Authorization": f"Basic {b64_auth_str}"}

    def _make_request(
        self, 
        endpoint: str, 
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        url = f"{self._base_url}{endpoint}"
        response = requests.get(url, headers=self._auth_header, params=params)
        
        try:
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

    def get_fixtures_v3(
        self, 
        sport_id: int, 
        league_ids: Optional[List[int]] = None,
        is_live: Optional[bool] = None, 
        since: Optional[int] = None,
        event_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        params = {
            "sportId": sport_id,
            "leagueIds": ",".join(map(str, league_ids)) if league_ids else None,
            "isLive": 1 if is_live else None,
            "since": since,
            "eventIds": ",".join(map(str, event_ids)) if event_ids else None
        }
        return self._make_request("/v3/fixtures", params)

    def get_straight_line_v2(
        self, 
        league_id : int,
        handicap: float = None,
        odds_format: str = "American",
        sport_id: int = None,
        event_id: int = None,
        period_number: int = None,
        bet_type: str = None,
        team : str = None,
        side: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {
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
        return self._make_request("/v2/line", params)

    def get_sports_v3(self) -> Dict[str, Any]:
        return self._make_request("/v3/sports")

    def get_leagues_v3(self, sport_id: int) -> Dict[str, Any]:
        params = {"sportId": sport_id}
        return self._make_request("/v3/leagues", params)

