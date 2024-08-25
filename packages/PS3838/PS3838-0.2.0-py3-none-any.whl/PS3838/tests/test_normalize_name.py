from PS3838._utils.tools_code import normalize_name


def test_normalize_name_all_lowercase():
    assert normalize_name("example") == "example"

def test_normalize_name_all_uppercase():
    assert normalize_name("EXAMPLE") == "example"

def test_normalize_name_mixed_case():
    assert normalize_name("ExAmPlE") == "example"

def test_normalize_name_with_spaces_in_the_middle():
    assert normalize_name("example name") == "examplename"

def test_normalize_name_with_spaces_at_the_end():
    assert normalize_name("example ") == "example"

def test_normalize_name_with_spaces_at_the_beginning():
    assert normalize_name(" example") == "example"

def test_normalize_name_with_punctuation():
    assert normalize_name("example.name!") == "examplename"

def test_normalize_name_with_numbers():
    assert normalize_name("example123") == "example123"

def test_normalize_name_mixed_characters():
    assert normalize_name("Exa mple123!") == "example123"

def test_normalize_name_empty_string():
    assert normalize_name("") == ""

def test_normalize_name_only_special_characters():
    assert normalize_name("!!!") == ""

def test_normalize_name_with_underscore():
    assert normalize_name("example_name") == "examplename"

def test_normalize_name_with_hyphen():
    assert normalize_name("example-name") == "examplename"

def test_normalize_name_with_unicode_characters():
    assert normalize_name("exámplè") == "exámplè"
    

