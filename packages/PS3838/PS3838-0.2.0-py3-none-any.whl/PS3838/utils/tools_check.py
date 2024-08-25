from datetime import datetime
from typing import Any, Dict, List

from PS3838._utils.errors import CredentialError, ParameterError


def check_credentials(credentials : Dict[str, str] = None) -> None:
    if not credentials:
        raise CredentialError("Credentials are missing")
    if not isinstance(credentials, dict):
        raise CredentialError("Credentials must be a dictionary")
    if not all(key in credentials for key in ["username", "password"]):
        raise CredentialError("Credentials must contain 'username' and 'password' keys")
    if not all(isinstance(credentials[key], str) for key in ["username", "password"]):
        raise CredentialError("Credentials 'username' and 'password' must be strings")



def check_list_matches(list_matches : List[Dict[str, Any]] = None, to_bet : bool = False) -> None:
    # check if the list of matches is provided
    if not list_matches:
        raise ParameterError("The list of matches is missing")
    
    # check if the list of matches is a list
    if not isinstance(list_matches, list):
        raise ParameterError("The list of matches must be a list")
    
    # check if to_bet is a boolean
    if type(to_bet) != bool:
        raise ParameterError("Parameter to_bet must be a boolean")
    
    # check each match in the list of matches
    for match in list_matches:
        check_match(match, to_bet=to_bet)


def check_match(match : Dict[str, Any], to_bet : bool = False) -> None:
    if not isinstance(match, dict):
        raise ParameterError("Each match must be a dictionary")
    if "league" not in match.keys():
        raise ParameterError(f"Parameter \"league\" is missing for at least one match")
    if "team1" not in match.keys():
        raise ParameterError(f"Parameter \"team1\" is missing for at least one match")
    if "team2" not in match.keys():
        raise ParameterError(f"Parameter \"team2\" is missing for at least one match")
    if type(match["league"]) not in [str, int]:
        raise ParameterError(f"\"league\" for match  {match['team1']} - {match['team2']}  must be a string or an integer")
    if type(match["team1"]) != str:
        raise ParameterError(f"\"team1\" for match  {match['team1']} - {match['team2']}  must be a string")
    if type(match["team2"]) != str:
        raise ParameterError(f"\"team2\" for match  {match['team1']} - {match['team2']}  must be a string")
    if "date" in match.keys() and type(match["date"]) != datetime:
        raise ParameterError(f"Date for match  {match['team1']} - {match['team2']}  must be a datetime object")
    if to_bet:
        if "result" not in match.keys():
            raise ParameterError(f"Result for match  {match['team1']} - {match['team2']}  is missing")
        if "amount" not in match.keys():
            raise ParameterError(f"Amount for match  {match['team1']} - {match['team2']}  is missing")
        if "odd_min" not in match.keys():
            raise ParameterError(f"Minimum odd for match  {match['team1']} - {match['team2']}  is missing")
        if type(match["result"]) != int or (type(match["result"]) == int and match["result"] not in [0, 1, 2]):
            raise ParameterError(f"Result for match  {match['team1']} - {match['team2']}  must be an integer in [0, 1, 2]")
        if (type(match["amount"]) != float and type(match["amount"]) != int) or (((type(match["amount"]) == int) or (type(match["amount"]) == float)) and match["amount"] < 5):
            raise ParameterError(f"Amount for match  {match['team1']} - {match['team2']}  must be an integer or a float greater than 5")
        if type(match["odd_min"]) != float or (type(match["odd_min"]) == float and match["odd_min"] < 1):
            raise ParameterError(f"Minimum odd for match {match['team1']} - {match['team2']}  must be a float greater than 1")
        
