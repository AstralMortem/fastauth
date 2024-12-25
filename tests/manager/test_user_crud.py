from contextlib import nullcontext as does_not_raise
from unittest.mock import MagicMock, AsyncMock
from fastauth.repositories import AbstractUserRepository
from fastauth.manager import BaseAuthManager
import pytest
from fastauth.exceptions import UserNotFound, UserAlreadyExists
from fastauth.schema import BaseUserUpdate


@pytest.fixture()
def auth_manager(fastauth_config):
    manager = BaseAuthManager(
        config=fastauth_config,
        user_repository=AsyncMock(spec=AbstractUserRepository),
        rp_repository=None,
        oauth_repository=None,
    )
    return manager


check_verification = [
    ((True, True), (True, True), does_not_raise()),
    ((False, True), (True, False), pytest.raises(UserNotFound)),
    ((True, False), (False, True), pytest.raises(UserNotFound)),
    ((True, True), (False, False), does_not_raise()),
    ((True, False), (True, False), does_not_raise()),
]


@pytest.mark.parametrize("user_fields,test_fields,raises", check_verification)
@pytest.mark.asyncio
async def test_user_check_verification(user_fields, test_fields, raises, auth_manager):
    user = MagicMock()

    with raises as error:
        user.is_active = user_fields[0]
        user.is_verified = user_fields[1]

        result = await auth_manager._check_user_verification(
            user, test_fields[0], test_fields[1]
        )
        assert result == user


@pytest.mark.asyncio
async def test_get_user_id(auth_manager):
    auth_manager.user_repo.get_by_id = AsyncMock(side_effect=lambda uid: uid)
    result = await auth_manager.get_user("user-id")
    assert result == "user-id"

    # Raise
    auth_manager.user_repo.get_by_id = AsyncMock(return_value=None)
    with pytest.raises(UserNotFound):
        await auth_manager.get_user("user-id")


@pytest.mark.asyncio
async def test_get_user_by_email(auth_manager):
    auth_manager.user_repo.get_by_email = AsyncMock(side_effect=lambda email: email)
    result = await auth_manager.get_user_by_email("user@email.com")
    assert result == "user@email.com"

    auth_manager.user_repo.get_by_email = AsyncMock(return_value=None)
    with pytest.raises(UserNotFound):
        await auth_manager.get_user_by_email("user@email.com")


@pytest.mark.asyncio
async def test_user_patch(auth_manager):
    auth_manager.get_user = AsyncMock(side_effect=lambda uid: uid)
    auth_manager.user_repo.update = AsyncMock(
        side_effect=lambda user, data: (user, data)
    )
    user_data = BaseUserUpdate(username="user")

    result_user, result_data = await auth_manager.patch_user("user-id", user_data)
    assert result_user == "user-id"
    assert result_data == user_data.model_dump(
        exclude_unset=True, exclude_defaults=True
    )

    auth_manager.user_repo.update.assert_called_once_with(
        "user-id", user_data.model_dump(exclude_unset=True, exclude_defaults=True)
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_data, update_data, existing_email, expected_exception, expected_update",
    [
        # Case 1: Valid email update
        (
            {"email": "old_email@example.com"},
            {"email": "new_email@example.com"},
            None,
            None,
            {"email": "new_email@example.com", "is_verified": False},
        ),
        # Case 2: Email already exists
        (
            {"email": "old_email@example.com"},
            {"email": "existing_email@example.com"},
            "existing_email@example.com",
            UserAlreadyExists,
            None,
        ),
        # Case 3: Valid password update
        (
            {"email": "user@example.com"},
            {"password": "new_secure_password"},
            None,
            None,
            {"hashed_password": "hashed_password"},
        ),
        # Case 4: Update other fields
        (
            {"email": "user@example.com"},
            {"first_name": "John", "last_name": "Doe"},
            None,
            None,
            {"first_name": "John", "last_name": "Doe"},
        ),
    ],
)
async def test_update_user(
    user_data,
    update_data,
    existing_email,
    expected_exception,
    expected_update,
    auth_manager,
):
    # Arrange
    user = MagicMock(**user_data)
    request = MagicMock()
    auth_manager.user_repo.get_by_email = AsyncMock(
        return_value=MagicMock() if existing_email else None
    )
    auth_manager.password_helper = MagicMock()
    auth_manager.password_helper.hash.return_value = "hashed_password"

    # Act
    if expected_exception:
        with pytest.raises(expected_exception):
            await auth_manager._update_user(user, update_data, request)
    else:
        await auth_manager._update_user(user, update_data, request)

        # Assert
        if "email" in update_data and update_data["email"] != user_data["email"]:
            auth_manager.user_repo.get_by_email.assert_called_once_with(
                update_data["email"]
            )

        if "password" in update_data:
            auth_manager.password_helper.hash.assert_called_once_with(
                update_data["password"]
            )

        auth_manager.user_repo.update.assert_called_once_with(user, expected_update)


@pytest.mark.asyncio
async def test_delete_user(auth_manager):
    auth_manager.get_user = AsyncMock(side_effect=lambda user: user)
    result = await auth_manager.delete_user("user-id")
    assert result == None

    auth_manager.user_repo.delete.assert_called_once_with("user-id")
