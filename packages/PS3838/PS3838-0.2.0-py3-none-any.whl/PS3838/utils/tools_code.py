from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import Levenshtein

from PS3838._PS3838Bet import Bet
from PS3838._PS3838Retrieve import Retrieve
from PS3838._telegram.telegram_bot import CustomLogger
from PS3838._utils.constants import ID_SOCCER
from PS3838._utils.errors import RetrieveMatchError


def retrieve_matches(
    list_matches : List[Dict[str, Any]],
    api_retrieve : Retrieve,
    logger : Optional[CustomLogger] = None,
    *args, 
    **kwargs
) -> List[Dict[str, Any]]:
    """
    This function retrieves the matches from the list of matches provided. It retrieves the matches one by one and appends them to a list of matches found.
    
    Parameters:
        list_matches : List[Dict[str, Any]] : List of matches to retrieve.
        api_retrieve : Retrieve : API object to retrieve the matches
        logger : Optional[CustomLogger] : Logger to log the results
    
    Returns:
        matches_found : List[Dict[str, Any]] : List of matches found
    """

    # Retrieve the matches
    matches_found = []
    for match in list_matches:
        
        try : 
            # Try to find the match that corresponds to the parameters
            match_found= retrieve_match(api_retrieve, league=match["league"], name_team1=match["team1"], name_team2=match["team2"], date=match["date"] if "date" in match.keys() else None, result=match["result"] if "result" in match.keys() else None, amount=match["amount"] if "amount" in match.keys() else None, odd_min=match["odd_min"] if "odd_min" in match.keys() else None, logger=logger)


            # Append the match to the list of matches found
            matches_found.append(match_found)
            if logger:
                logger.info(f"Match found for {match_found['home']} - {match_found['away']}")

        except Exception as e:
            if logger:
                logger.error(f"Error retrieving match for {match['team1']} - {match['team2']} : {e}")
            continue

    return matches_found

def retrieve_match(
    api_retrieve : Retrieve,
    league : str | int, 
    name_team1 : str, 
    name_team2 : str, 
    date : Optional[datetime] = None, 
    result : Optional[int] = None,
    amount : Optional[int] = None,
    odd_min : Optional[float] = None,
    logger : Optional[CustomLogger] = None,
    *args, 
    **kwargs
) -> Dict[str, Any]:
    """
    This function retrieves a match from the API based on the parameters provided. It retrieves the leagues, the matches in the league, and then finds the match that corresponds to the parameters.
    
    Parameters:
        api_retrieve : Retrieve : API object to retrieve the matches
        league : str | int : League name or ID (better to put the ID)
        name_team1 : str : Name of the first team
        name_team2 : str : Name of the second team
        date : Optional[datetime] : Date of the match
        result : Optional[int] : Result of the match (1 = team1 win, 2 = team2 win, 0 = draw)
        amount : Optional[int] : Amount to bet on the match
        odd_min : Optional[float] : Minimum odds to bet on the match
        logger : Optional[CustomLogger] : Logger to log the results
        
    Returns:
        match : Dict[str, Any] : Match found
    """

    # Find the leagues
    leagues = api_retrieve.get_leagues_v3(sport_id=ID_SOCCER)

    # Find the ID of the league
    league_id = find_league_id(leagues, league, logger)

    # Find the matches in the league
    fixtures = api_retrieve.get_fixtures_v3(sport_id=ID_SOCCER, league_ids=[league_id])

    # Keep only the elements where 'statut' = 'O' which means the match is open
    fixtures = [match for match in fixtures["league"][0]["events"] if match["status"] == "O"]

    print(fixtures)

    # Find the match
    match = find_match(fixtures, name_team1, name_team2, date, logger)

    # Verify if the parameter result is correct
    result = verify_result(match, name_team1, name_team2, result, logger)

    # Add the league ID to the match, the result, the amount and the minimum odds that are fundamentals parameters if we want to bet afterwards
    match["league"] = league_id
    match["result"] = result
    match["amount"] = amount
    match["odd_min"] = odd_min

    return match

def get_team_odds(api_retrieve: Retrieve, match: Dict[str, Any], team: str) -> Dict[str, Any]:
    """
    This function retrieves the odds for a specific team in a match.

    Parameters:
        api_retrieve : Retrieve : API object to retrieve the odds
        match : Dict[str, Any] : Match to retrieve the odds for
        team : str : Team to retrieve the odds for

    Returns:
        odds : Dict[str, Any] : Odds for the team
    """
    odds_response = api_retrieve.get_straight_line_v2(
        league_id=match["league"],
        handicap=0,
        odds_format="Decimal",
        sport_id=ID_SOCCER,
        event_id=match["id"],
        period_number=match.get("period_number", 0),
        bet_type="MONEYLINE",
        team=team
    )

    return odds_response.get("price", 0), odds_response.get("lineId", 0)
    
def normalize_name(name : str) -> str:
    """
    This function normalizes a name by removing all special characters and converting it to lowercase.
    """
    return ''.join(e for e in name.lower() if e.isalnum())


def find_best_match(name: str, candidates: list[str], cutoff : float = 0.5) -> str:
    """
    This function finds the best match for a name in a list of candidates. It uses the Levenshtein distance to calculate the similarity between the name and the candidates. It is useful when the name of sport_api is not exactly the same as the name on PS3838. The cutoff parameter is used to filter the candidates that are too different from the name.
    """
    normalized_name = normalize_name(name)
    normalized_candidates = [normalize_name(candidate) for candidate in candidates]

    best_match = None
    highest_similarity = -1

    for candidate in normalized_candidates:
        similarity = Levenshtein.ratio(normalized_name, candidate)
        if similarity > highest_similarity and similarity >= cutoff:
            highest_similarity = similarity
            best_match = candidate

    if best_match:
        best_match_index = normalized_candidates.index(best_match)
        return candidates[best_match_index]

    return None

def find_match(
    fixtures : list[Dict[str, Any]], 
    name_team1 : str, 
    name_team2 : str, 
    date : datetime = None, 
    logger : CustomLogger = None
) -> Dict[str, Any]:
    """
    This function finds the match that corresponds to the team names and the date provided. It first tries to have the perfect match between team1 and team2 and the date, and then tries a lighter version without the date.
    
    Parameters:
        fixtures : list[Dict[str, Any]] : List of available matches returned by PS3838.
        name_team1 : str : Name of the first team
        name_team2 : str : Name of the second team
        date : datetime : Date of the match
        logger : CustomLogger : Logger to log the results
        
    Returns:
        match : Dict[str, Any] : Match found
    """
    # Find the candidates for the team names
    candidates_home = []
    candidates_away = []
    for match in fixtures:
        candidates_home.append(match["home"])
        candidates_away.append(match["away"])

    match = None
    # Find the match
    for fixture in fixtures:
        if (find_best_match(name_team1, candidates_home) == fixture["home"] and find_best_match(name_team2, candidates_away) == fixture["away"]) or (find_best_match(name_team1, candidates_away) == fixture["away"] and find_best_match(name_team2, candidates_home) == fixture["home"]) and datetime.fromisoformat(fixture["starts"].replace('Z','')) == date:
            match = fixture
            break
        elif (find_best_match(name_team1, candidates_home) == fixture["home"] and find_best_match(name_team2, candidates_away) == fixture["away"]) or (find_best_match(name_team1, candidates_away) == fixture["away"] and find_best_match(name_team2, candidates_home) == fixture["home"]):
            match = fixture
            break
        
    if not match:
        if logger:
            logger.error(f"Match not found for {name_team1} - {name_team2}")
        raise RetrieveMatchError("Match not found")
    
    return match

def verify_result(
    match : Dict[str, Any],
    name_team1 : str, 
    name_team2 : str, 
    result : int, 
    logger : CustomLogger = None
) -> int:
    """
    This function verifies if the result corresponds to the home team or the away team, and changes it if necessary.
    For example if we entered Marseille - Lens with result 1 and the actual match is Lens - Marseille, the function will return 2.
    
    Parameters:
        match : Dict[str, Any] : Match found
        name_team1 : str : Name of the first team
        name_team2 : str : Name of the second team
        result : int : Result of the match (1 = team1 win, 2 = team2 win, 0 = draw)
        logger : CustomLogger : Logger to log the results
        
    Returns:
        int : 1 if the result corresponds to the home team, 2 if the result corresponds to the away team, 0 if the result corresponds to a draw
    """
    if result is not None:
        if result == 1:
            if (find_best_match(match["home"], [name_team1, name_team2]) == name_team1) and (find_best_match(match["away"], [name_team1, name_team2]) == name_team2):
                return 1
            elif (find_best_match(match["away"], [name_team1, name_team2]) == name_team1) and (find_best_match(match["home"], [name_team1, name_team2]) == name_team2):
                return 2
            elif (find_best_match(match["home"], [name_team1, name_team2]) == name_team1) or (find_best_match(match["away"], [name_team1, name_team2]) == name_team2):
                return 1
            elif (find_best_match(match["away"], [name_team1, name_team2]) == name_team1) or (find_best_match(match["home"], [name_team1, name_team2]) == name_team2):
                return 2
            else:
                if logger:
                    logger.error(f"Error while verifying if the result 1 corresponds to the home team")
                raise RetrieveMatchError("Error while verifying if the result 1 corresponds to the home team")
        elif result == 2:
            if (find_best_match(match["home"], [name_team1, name_team2]) == name_team1) and (find_best_match(match["away"], [name_team1, name_team2]) == name_team2):
                return 2
            elif (find_best_match(match["away"], [name_team1, name_team2]) == name_team1) and (find_best_match(match["home"], [name_team1, name_team2]) == name_team2):
                return 1
            elif (find_best_match(match["home"], [name_team1, name_team2]) == name_team1) or (find_best_match(match["away"], [name_team1, name_team2]) == name_team2):
                return 2
            elif (find_best_match(match["away"], [name_team1, name_team2]) == name_team1) or (find_best_match(match["home"], [name_team1, name_team2]) == name_team2):
                return 1
            else:
                if logger:
                    logger.error(f"Error while verifying if the result 2 corresponds to the home team")
                raise RetrieveMatchError("Error while verifying if the result 2 corresponds to the home team")
        else:
            return 0
    else:
        return None
    

# To be corrected in the future
def find_league_id(
    leagues: Dict[str, Any], 
    league: str | int, 
    logger : CustomLogger = None
) -> int:
    """
    This function finds the ID of the league based on the name or the ID provided.
    The possibility of putting a string will be removed in the future to use directly the ID of the league."""
    if isinstance(league, int):
        # If league is an integer, directly find the matching ID
        for element in leagues.get("leagues", []):
            if element["id"] == league:
                return element["id"]
    else:
        # If league is a string, find the best matching league name
        league_names = [element["name"] for element in leagues.get("leagues", [])]
        league_name = find_best_match(league, league_names)
        for element in leagues.get("leagues", []):
            if element["name"] == league_name:
                return element["id"]
    if logger:
        logger.error(f"League not found")
    raise RetrieveMatchError("League not found")

def change_date(date : str, days : int, hours : int) -> str:
    """
    This function changes the date by adding days and hours to it. It is useful to search for bets that were placed from 25 days in the past to 1 day in the future (as it is done in the function is_already_bet).
    """
    date = datetime.fromisoformat(date.replace('Z',''))
    date = date + timedelta(days=days, hours=hours)
    return date.isoformat() + 'Z'

def place_bets(
    match_odds : List[Tuple[Dict[str, Any], Dict[str, Any]]], 
    bet : Bet, 
    logger : CustomLogger = None
):
    """
    This function places the bets for the matches found with the odds provided. It verifies if the odds are not too low and if the bet is not already placed. Then in function of the parameter result, it places the bet on the home team, the away team or the draw.
    
    Parameters:
        match_odds : List[Tuple[Dict[str, Any], Dict[str, Any]]] : List of matches found with the odds
        bet : Bet : API object to place the bets
        logger : CustomLogger : Logger to log the results
    """
    for match, odds in match_odds:
        if is_already_bet(bet, match):
            if logger:
                logger.warning(f"Bet already placed for match {match['id']} : {match['home']} - {match['away']}, skipping bet")
            continue
        if match["result"] == 1:
            if not verify_odds(match["odd_min"], odds["team1_odds"]):
                if logger:
                    logger.warning(f"Odds for match {match['id']} are finally too low, skipping bet")
                continue
            bet.place_bet(stake=match["amount"], line_id=match["line_id"], sport_id=ID_SOCCER, event_id=match["id"], period_number=0, team="TEAM1")
        elif match["result"] == 2:
            if not verify_odds(match["odd_min"], odds["team2_odds"]):
                if logger:
                    logger.warning(f"Odds for match {match['id']} are finally too low, skipping bet")
                continue
            bet.place_bet(stake=match["amount"], line_id=match["line_id"], sport_id=ID_SOCCER, event_id=match["id"], period_number=0, team="TEAM2")
        elif match["result"] == 0:
            if not verify_odds(match["odd_min"], odds["draw_odds"]):
                if logger:
                    logger.warning(f"Odds for match {match['id']} are finally too low, skipping bet")
                continue
            bet.place_bet(stake=match["amount"], line_id=match["line_id"], sport_id=ID_SOCCER, event_id=match["id"], period_number=0, team="Draw")
        if is_already_bet(bet, match):
            if logger:
                logger.info(f"Bet placed successfully for match {match['home']} - {match['away']}")

def verify_odds(odd_min : float, real_odd : float) -> bool:
    """
    This function verifies if the real odd is higher than the minimum odd required to place the bet. It is useful to check this right before placing the bet, to avoid placing a bet with too low odds.
    """
    return real_odd >= odd_min

def is_already_bet(api_bet : Bet, match : Dict[str, Any]) -> bool:
    """
    This function verifies if the bet is already placed for the match provided. It retrieves the bets placed in the past and checks if the bet is here. Also depending on the status of the bet, it returns True or False.
    """
    bets = api_bet.get_bets_v3(betlist='ALL', from_date=change_date(date=match["starts"], days=-25, hours=0), to_date=change_date(date=match["starts"], days=1, hours=0))
    if "straightBets" in bets.keys():
        straights = bets["straightBets"]
        for bet in straights:
            if (bet["eventId"] == match["id"]) and (bet['betStatus'] == 'LOSE' or bet['betStatus'] == 'ACCEPTED' or bet['betStatus'] == 'CANCELLED' or bet['betStatus'] == 'WON' or bet['betStatus'] == 'REFUNDED' or bet['betStatus'] == 'PENDING_ACCEPTANCE'):
                return True
    
    return False