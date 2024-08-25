from typing import Any, Dict, List, Optional

from PS3838._PS3838Bet import Bet
from PS3838._PS3838Retrieve import Retrieve
from PS3838._telegram.telegram_bot import CustomLogger
from PS3838._utils.tools_check import check_credentials, check_list_matches
from PS3838._utils.tools_code import (get_team_odds, place_bets,
                                      retrieve_matches)


class PS3838AutomatedBet():
    def __init__(
        self,
        credentials : Dict[str, str] = None,
        list_matches : List[Dict[str, Any]] = None,
        logger_active: Optional[bool] = True,
        to_bet: Optional[bool] = False,
        *args,
        **kwargs
    ):
        """
        This class is used to retrieve the odds for a list of matches or to place bets on the PS3838 API. It uses the Retrieve and Bet classes to connect to the API and retrieve the odds or place the bets. It also uses a CustomLogger to log the information.
        
        Parameters:
            credentials (Dict[str, str]): The credentials to connect to the PS3838 API. 
                Example: {"username": "my_username", "password": "my_password"}
            list_matches (List[Dict[str, Any]]): A list of matches to retrieve the odds for or to place the bets for.
                Example: [{"league" : 2036, "team1" : "Montpellier", "team2" : "Paris Saint-Germain", "date" : datetime(2024, 8, 17, 17, 0, 0), "result" : 2, "amount" : 5, "odd_min" : 1.05}, ...]. Note that the parameters "result", "amount" and "odd_min" are optional and only used when placing bets.
            logger_active (bool): A boolean to activate the logger. Default is True.
            to_bet (bool): A boolean to know if we want to retrieve the odds or place the bets. Default is False.
        """

        self.credentials = credentials
        self.list_matches = list_matches
        self.logger_active = logger_active
        self.to_bet = to_bet
        self.retrieve = None
        self.bet = None
        self.logger = None

        self._initiate()

    def _initiate(self):
        # Create the logger. 
        if self.logger_active:
            custom_logger = CustomLogger(name="PS3838", log_file="PS3838.log", func="betting" if self.to_bet else "retrieving", credentials=self.credentials)
            self.logger = custom_logger.get_logger()

        # Check if the parameters are provided and valid (Raise a CredentialError if not), and check if the list of matches is valid (Raise a ParameterError if not)
        check_credentials(self.credentials)
        check_list_matches(self.list_matches, to_bet=self.to_bet)

        # Create the Bet and Retrieve objects
        self.bet = Bet(credentials=self.credentials)
        self.retrieve = Retrieve(credentials=self.credentials)


    #############################
    #        Retrieving         #
    #############################

    def retrieving(self) -> List[List[Dict[str, Any]]]:
        """
        This function retrieves the odds for a given list of matches. Several functions are used to find each match and their corresponding odds.
            
        Returns:
            List[List[Dict[str, Any]]]: A list of matches with their corresponding odds.
                Example: [({'id': 1595460299, 'starts': '2024-08-23T18:45:00Z', 'home': 'Paris Saint-Germain', 'away': 'Montpellier HSC', 'rotNum': '3121', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 545200449, 'league': 2036, 'result': 1, 'amount': 5, 'odd_min': 1.05, 'line_id': 2650184231}, {'team1_odds': 1.309, 'draw_odds': 6.14, 'team2_odds': 8.47}), ...]
        """

        # Retrieve the matches
        matches = retrieve_matches(self.list_matches, self.retrieve, self.logger)

        # Retrieve the odds for each match
        match_odds = []
        for match in matches:
            try:
                team1_odds, match["line_id"] = get_team_odds(self.retrieve, match, "Team1")
                team2_odds, _ = get_team_odds(self.retrieve, match, "Team2")
                draw_odds, _ = get_team_odds(self.retrieve, match, "Draw")
                
                # Append the match and odds to the list "match_odds"
                match_odds.append((match, 
                    {
                        "team1_odds": team1_odds,
                        "draw_odds": draw_odds,
                        "team2_odds": team2_odds,
                    }
                ))
                
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error retrieving odds for match {match['event_id']}: {e}")
        
        if self.logger:
            self.logger.info(f"Retrieved odds for {len(match_odds)} match(es)" if len(match_odds) > 0 else "No matches found")
        return match_odds


    #############################
    #         Betting           #
    #############################

    def betting(self) -> List[List[Dict[str, Any]]] | None:
        """
        This function places bets on the PS3838 API for a given list of matches. It retrieves the odds for each match and then places the bets under some conditions (bet not already placed, odds above a certain threshold, etc.).
 
        Returns:
            List[List[Dict[str, Any]]] | None: A list of matches with their corresponding odds if the bets were placed, None otherwise.
                Example: [({'id': 1595460299, 'starts': '2024-08-23T18:45:00Z', 'home': 'Paris Saint-Germain', 'away': 'Montpellier HSC', 'rotNum': '3121', 'liveStatus': 2, 'status': 'O', 'parlayRestriction': 2, 'altTeaser': False, 'resultingUnit': 'Regular', 'betAcceptanceType': 0, 'version': 545200449, 'league': 2036, 'result': 1, 'amount': 5, 'odd_min': 1.05, 'line_id': 2650184231}, {'team1_odds': 1.309, 'draw_odds': 6.14, 'team2_odds': 8.47}), ...]
        """

        # Check if there is maintenance
        maintenance = self.bet.check_maintenance()

        if maintenance["status"] == 'ALL_BETTING_ENABLED':
            try:
                # Retrieve the odds with the matches
                match_odds = self.retrieving()

                # Place the bets
                place_bets(match_odds, self.bet, logger=self.logger)

            except Exception as e:
                if self.logger:
                    self.logger.error(f"Error placing bets: {e}")
        else:
            if self.logger:
                self.logger.info("Maintenance in progress, no bets placed. Try another time")

        return match_odds if match_odds else None
    
    def __call__(self, *args: Any, **kwds: Any) -> Any:
        if self.to_bet:
            return self.betting()
        return self.retrieving()