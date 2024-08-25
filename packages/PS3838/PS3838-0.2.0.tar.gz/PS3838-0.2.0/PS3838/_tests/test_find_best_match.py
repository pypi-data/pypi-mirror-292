from PS3838._utils.tools_code import find_best_match


def test_find_best_match_exact_match():
    assert find_best_match("Argentina", ["Argentina", "Brazil", "Colombia"]) == "Argentina"

def test_find_best_match_case_insensitive_match():
    assert find_best_match("argentina", ["Argentina", "Brazil", "Colombia"]) == "Argentina"

def test_find_best_match_with_spaces():
    assert find_best_match("Argen tina", ["Argentina", "Brazil", "Colombia"]) == "Argentina"

def test_find_best_match_with_punctuation():
    assert find_best_match("Argentina!", ["Argentina", "Brazil", "Colombia"]) == "Argentina"

def test_find_best_match_partial_match():
    assert find_best_match("Argen", ["Argentina", "Brazil", "Colombia"]) == "Argentina"

def test_find_best_match_no_close_match():
    assert find_best_match("Chile", ["Argentina", "Brazil", "Colombia"]) is None

def test_find_best_match_empty_candidates():
    assert find_best_match("Argentina", []) is None

def test_find_best_match_empty_name():
    assert find_best_match("", ["Argentina", "Brazil", "Colombia"]) is None

def test_find_best_match_multiple_close_matches():
    assert find_best_match("Argentin", ["Argentina", "Argentinos", "Brazil"]) == "Argentina"

def test_find_best_match_with_numbers():
    assert find_best_match("Argentina123", ["Argentina", "Brazil123", "Colombia"]) == "Argentina"

def test_find_best_match_all_special_characters():
    assert find_best_match("@rgentina!", ["Argentina", "Brazil", "Colombia"]) == "Argentina"

def test_find_best_match_cutoff_no_match():
    assert find_best_match("Arg", ["Argentina", "Brazil", "Colombia"]) == "Argentina"

def test_find_best_match_levenshtein():
    assert find_best_match("Arg", ["Argentina", "Brazil", "Colombia"]) == "Argentina"
    assert find_best_match("Brazil", ["Argentina", "Brazil", "Colombia"]) == "Brazil"
    assert find_best_match("Chil", ["Argentina", "Brazil", "Colombia", "Chile"]) == "Chile"
    assert find_best_match("Chile", ["Argentina", "Brazil", "Colombia"]) is None