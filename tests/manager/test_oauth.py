from unittest.mock import AsyncMock, MagicMock, Mock
import pytest

from fastauth import exceptions
from fastauth.manager import BaseAuthManager
from fastauth.repositories import AbstractUserRepository, AbstractOAuthRepository


@pytest.fixture
def auth_manager(fastauth_config):
    manager = BaseAuthManager(
        config=fastauth_config,
        user_repository=AsyncMock(spec=AbstractUserRepository),
        rp_repository=None,
        oauth_repository=AsyncMock(spec=AbstractOAuthRepository),
    )
    return manager


@pytest.mark.asyncio
async def test_get_user_by_oauth(auth_manager):
    auth_manager.oauth_repo.get_user = AsyncMock(side_effect=lambda x, y: (x, y))
    x, y = await auth_manager.get_user_by_oauth_account("x", "y")
    assert x == "x"
    assert y == "y"

    with pytest.raises(exceptions.UserNotFound):
        auth_manager.oauth_repo.get_user = AsyncMock(return_value=None)
        await auth_manager.get_user_by_oauth_account("x", "y")


@pytest.mark.asyncio
async def test_oauth_callback_existing_user_association_error(auth_manager):
    # Arrange
    oauth_name = "google"
    account_id = "12345"
    account_email = "test@example.com"
    access_token = "token123"

    auth_manager.oauth_repo.get_user.side_effect = exceptions.UserNotFound
    auth_manager.user_repo.get_by_email.return_value = MagicMock(oauth_accounts=[])

    # Act & Assert
    with pytest.raises(exceptions.UserAlreadyExists):
        await auth_manager.oauth_callback(
            oauth_name,
            access_token,
            account_id,
            account_email,
            associate_by_email=False,
        )


@pytest.mark.asyncio
async def test_oauth_user_exists_add_new_oauth(auth_manager):
    oauth_name = "google"
    account_id = "12345"
    account_email = "test@example.com"
    access_token = "token123"

    async def set_oauth(user, data):
        user.oauth_accounts.append(MagicMock(**data))
        return user

    auth_manager.oauth_repo.get_user.side_effect = exceptions.UserNotFound
    auth_manager.user_repo.get_by_email.return_value = MagicMock(oauth_accounts=[])
    auth_manager.oauth_repo.add_oauth_account.side_effect = set_oauth

    result = await auth_manager.oauth_callback(
        oauth_name,
        access_token,
        account_id,
        account_email,
        associate_by_email=True,
    )

    assert result.oauth_accounts[0].oauth_name == oauth_name
    assert result.oauth_accounts[0].account_id == account_id
    assert result.oauth_accounts[0].account_email == account_email
    assert result.oauth_accounts[0].access_token == access_token


@pytest.mark.asyncio
async def test_oauth_user_exists_and_update_oauth_accounts(auth_manager):
    async def update_user(user, oauth, data):
        for key, val in data.items():
            setattr(oauth, key, val)
        user.oauth_accounts[0] = oauth
        return user

    auth_manager.oauth_repo.update_oauth_account.side_effect = update_user

    oauth_name = "google"
    account_id = "12345"
    account_email = "test@example.com"
    access_token = "token123"

    existed_oauth = MagicMock(account_id=account_id, oauth_name=oauth_name)
    user = MagicMock(oauth_accounts=[existed_oauth])

    auth_manager.oauth_repo.get_user.return_value = user

    result = await auth_manager.oauth_callback(
        oauth_name, access_token, account_id, account_email, associate_by_email=True
    )

    assert result == user
    assert result.oauth_accounts[0].account_id == account_id
    assert result.oauth_accounts[0].oauth_name == oauth_name
    assert result.oauth_accounts[0].access_token == access_token
    assert result.oauth_accounts[0].account_email == account_email


@pytest.mark.asyncio
async def test_oauth_new_user_creation(auth_manager):

    async def set_oauth(user, data):
        user.oauth_accounts.append(MagicMock(**data))
        return user

    async def set_user(data):
        return MagicMock(**data, oauth_accounts=[])

    auth_manager.password_helper.hash = Mock(return_value="password")
    auth_manager.oauth_repo.get_user.side_effect = exceptions.UserNotFound
    auth_manager.user_repo.get_by_email.side_effect = exceptions.UserNotFound
    auth_manager.user_repo.create.side_effect = set_user
    auth_manager.oauth_repo.add_oauth_account.side_effect = set_oauth

    oauth_name = "google"
    account_id = "12345"
    account_email = "test@example.com"
    access_token = "token123"

    result = await auth_manager.oauth_callback(
        oauth_name,
        access_token,
        account_id,
        account_email,
        associate_by_email=True,
        is_verified_by_default=True,
    )

    assert result.email == account_email
    assert result.is_verified == True
    assert result.hashed_password == "password"
    oauth_account = result.oauth_accounts[0]
    assert oauth_account.oauth_name == oauth_name
    assert oauth_account.account_id == account_id
    assert oauth_account.account_email == account_email
    assert oauth_account.access_token == access_token


@pytest.mark.asyncio
async def test_oauth_new_user_create_with_role(auth_manager):

    async def set_oauth(user, data):
        user.oauth_accounts.append(MagicMock(**data))
        return user

    async def set_user(data):
        return MagicMock(**data, oauth_accounts=[])

    oauth_name = "google"
    account_id = "12345"
    account_email = "test@example.com"
    access_token = "token123"

    auth_manager.password_helper.hash = Mock(return_value="password")
    auth_manager.oauth_repo.get_user.side_effect = exceptions.UserNotFound
    auth_manager.user_repo.get_by_email.side_effect = exceptions.UserNotFound
    auth_manager.user_repo.create.side_effect = set_user
    auth_manager.oauth_repo.add_oauth_account.side_effect = set_oauth

    result = await auth_manager.oauth_callback(
        oauth_name,
        access_token,
        account_id,
        account_email,
        associate_by_email=True,
        is_verified_by_default=True,
        default_role=MagicMock(id="role_id"),
    )

    assert result.role_id == "role_id"
