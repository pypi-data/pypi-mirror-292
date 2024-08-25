import pytest

from PS3838._utils.tools_check import CredentialError, check_credentials


def test_check_credentials_success():
    credentials = {"username": "test_user", "password": "test_password"}
    try:
        check_credentials(credentials)
    except CredentialError:
        pytest.fail("check_credentials raised CredentialError unexpectedly!")

def test_check_credentials_missing_credentials():
    with pytest.raises(CredentialError, match="Credentials are missing"):
        check_credentials(None)

def test_check_credentials_not_a_dict():
    with pytest.raises(CredentialError, match="Credentials must be a dictionary"):
        check_credentials("username=test_user&password=test_password")

def test_check_credentials_missing_keys():
    credentials = {"username": "test_user"}
    with pytest.raises(CredentialError, match="Credentials must contain 'username' and 'password' keys"):
        check_credentials(credentials)

    credentials = {"password": "test_password"}
    with pytest.raises(CredentialError, match="Credentials must contain 'username' and 'password' keys"):
        check_credentials(credentials)

def test_check_credentials_keys_not_strings():
    credentials = {"username": 123, "password": "test_password"}
    with pytest.raises(CredentialError, match="Credentials 'username' and 'password' must be strings"):
        check_credentials(credentials)

    credentials = {"username": "test_user", "password": 456}
    with pytest.raises(CredentialError, match="Credentials 'username' and 'password' must be strings"):
        check_credentials(credentials)
