from unittest.mock import MagicMock, patch

import pytest
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher

from fastauth.utils.password import PasswordHelper


@pytest.fixture
def mock_password_hash():
    return MagicMock()


@pytest.fixture
def password_helper(mock_password_hash):
    return PasswordHelper(password_hash=mock_password_hash)


def test_password_helper_default():
    helper = PasswordHelper()
    assert isinstance(helper.password_hash, PasswordHash)
    assert isinstance(helper.password_hash.hashers[0], Argon2Hasher)
    assert isinstance(helper.password_hash.hashers[1], BcryptHasher)


def test_verify_and_update(password_helper, mock_password_hash):
    mock_password_hash.verify_and_update.return_value = (True, None)

    result = password_helper.verify_and_update("plain_password", "hashed_password")

    assert result == (True, None)
    mock_password_hash.verify_and_update.assert_called_once_with(
        "plain_password", "hashed_password"
    )


def test_hash(password_helper, mock_password_hash):
    mock_password_hash.hash.return_value = "hashed_password"

    result = password_helper.hash("plain_password")

    assert result == "hashed_password"
    mock_password_hash.hash.assert_called_once_with("plain_password")


def test_generate(password_helper):
    # Assuming secrets.token_urlsafe is used internally
    import secrets

    with patch("secrets.token_urlsafe", return_value="generated_token"):
        result = password_helper.generate()
        assert result == "generated_token"
