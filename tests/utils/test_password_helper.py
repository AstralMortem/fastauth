import pytest
from unittest.mock import MagicMock
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from fastauth.utils.password import PasswordHelper


def test_password_helper_default_initialization():
    helper = PasswordHelper()
    assert isinstance(helper.password_hash, PasswordHash)
    assert len(helper.password_hash.hashers) == 2
    assert any(isinstance(h, Argon2Hasher) for h in helper.password_hash.hashers)
    assert any(isinstance(h, BcryptHasher) for h in helper.password_hash.hashers)


def test_password_helper_hash():
    mock_password_hash = MagicMock()
    mock_password_hash.hash.return_value = "hashed_password"
    helper = PasswordHelper(password_hash=mock_password_hash)

    result = helper.hash("test_password")
    mock_password_hash.hash.assert_called_once_with("test_password")
    assert result == "hashed_password"


def test_password_helper_verify_and_update_success():
    mock_password_hash = MagicMock()
    mock_password_hash.verify_and_update.return_value = (True, None)
    helper = PasswordHelper(password_hash=mock_password_hash)

    result = helper.verify_and_update("plain_password", "hashed_password")
    mock_password_hash.verify_and_update.assert_called_once_with(
        "plain_password", "hashed_password"
    )
    assert result == (True, None)


def test_password_helper_verify_and_update_failure():
    mock_password_hash = MagicMock()
    mock_password_hash.verify_and_update.return_value = (False, None)
    helper = PasswordHelper(password_hash=mock_password_hash)

    result = helper.verify_and_update("plain_password", "wrong_hashed_password")
    mock_password_hash.verify_and_update.assert_called_once_with(
        "plain_password", "wrong_hashed_password"
    )
    assert result == (False, None)


def test_password_helper_verify_and_update_requires_update():
    mock_password_hash = MagicMock()
    mock_password_hash.verify_and_update.return_value = (True, "new_hashed_password")
    helper = PasswordHelper(password_hash=mock_password_hash)

    result = helper.verify_and_update("plain_password", "outdated_hashed_password")
    mock_password_hash.verify_and_update.assert_called_once_with(
        "plain_password", "outdated_hashed_password"
    )
    assert result == (True, "new_hashed_password")


def test_password_helper_generate():
    helper = PasswordHelper()
    token = helper.generate()
    assert isinstance(token, str)
    assert len(token) > 0
