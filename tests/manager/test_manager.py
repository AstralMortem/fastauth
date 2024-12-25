from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.security import OAuth2PasswordRequestForm
from jwt import PyJWTError

from fastauth import exceptions
from fastauth.manager import BaseAuthManager
from fastauth.repositories import (
    AbstractUserRepository,
    AbstractOAuthRepository,
    AbstractRolePermissionRepository,
)
from fastauth.schema import TokenResponse, BaseUserCreate
from fastauth.strategy.base import TokenStrategy
from fastauth.utils.jwt_helper import TokenHelperProtocol
from fastauth.utils.password import PasswordHelperProtocol


@pytest.fixture
def auth_manager(fastauth_config):
    manager = BaseAuthManager(
        config=fastauth_config,
        user_repository=AsyncMock(spec=AbstractUserRepository),
        rp_repository=AsyncMock(spec=AbstractRolePermissionRepository),
        oauth_repository=AsyncMock(spec=AbstractOAuthRepository),
    )
    return manager


@pytest.mark.asyncio
async def test_token_creation(auth_manager):
    async def set_strategy(user, type, **conf):
        return MagicMock(uid=user, type=type, **conf)

    strategy = AsyncMock()
    strategy.write_token.side_effect = set_strategy
    auth_manager.user_repo.get_by_id.side_effect = lambda user: user

    result = await auth_manager.create_token(
        "user-id",
        "access",
        strategy,
        max_age=3600,
        headers={"header": "header"},
        extra_data={"email": "email"},
    )

    assert result.uid == "user-id"
    assert result.type == "access"
    assert result.max_age == 3600
    assert result.extra_data["email"] == "email"
    assert result.headers["header"] == "header"


@pytest.mark.parametrize(
    "login_fields", ("email", "username", "phone", ["email", "username"])
)
@pytest.mark.asyncio
async def test_password_login_user_fetch(login_fields, auth_manager):
    user = MagicMock(id="user-id", hashed_password="password")

    auth_manager._config.USER_LOGIN_FIELDS = login_fields

    auth_manager.user_repo.get_by_email.return_value = user
    auth_manager.user_repo.get_by_username.return_value = user
    auth_manager.user_repo.get_by_field.return_value = user
    auth_manager.user_repo.get_by_fields.return_value = user
    auth_manager.user_repo.update.return_value = user

    auth_manager.password_helper = MagicMock(spec=PasswordHelperProtocol)
    auth_manager.password_helper.verify_and_update.return_value = (True, True)

    strategy = AsyncMock(spec=TokenStrategy)
    strategy.write_token.side_effect = lambda user, type: f"{user.id}_{type}"

    result = await auth_manager.password_login(
        OAuth2PasswordRequestForm(username="username", password="password"), strategy
    )

    assert isinstance(result, TokenResponse)
    assert result.access_token == f"{user.id}_access"
    assert result.refresh_token == f"{user.id}_refresh"


@pytest.mark.asyncio
async def test_password_login_failure(auth_manager):
    user = None
    auth_manager.user_repo.get_by_email.return_value = user
    auth_manager.user_repo.get_by_username.return_value = user
    auth_manager.user_repo.get_by_field.return_value = user
    auth_manager.user_repo.get_by_fields.return_value = user

    with pytest.raises(exceptions.UserNotFound):
        await auth_manager.password_login(
            OAuth2PasswordRequestForm(username="User", password="password"),
            AsyncMock(spec=TokenStrategy),
        )

    user = MagicMock(id="user-id", hashed_password="password")
    auth_manager.user_repo.get_by_email.return_value = user
    auth_manager.user_repo.get_by_username.return_value = user
    auth_manager.user_repo.get_by_field.return_value = user
    auth_manager.user_repo.get_by_fields.return_value = user

    auth_manager.password_helper = MagicMock(spec=PasswordHelperProtocol)
    auth_manager.password_helper.verify_and_update.return_value = (False, False)

    with pytest.raises(exceptions.UserNotFound):
        await auth_manager.password_login(
            OAuth2PasswordRequestForm(username="User", password="password"),
            AsyncMock(spec=TokenStrategy),
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_role, user_permissions, roles, permissions, expected_exception",
    [
        # Case: User has required role
        ("admin", [], ["admin"], [], None),
        # Case: User has required permission
        ("user", ["read"], [], ["read"], None),
        # Case: User has neither role nor permission
        ("user", ["read"], ["admin"], ["write"], exceptions.AccessDenied),
        # Case: User has overlapping permissions and roles
        ("admin", ["write"], ["admin"], ["read"], None),
        # Case: Empty required roles and permissions
        ("user", ["read"], [], [], None),
        ("user", ["write"], None, None, None),
    ],
)
async def test_check_access(
    user_role, user_permissions, roles, permissions, expected_exception, auth_manager
):
    # Mock user and dependencies
    user = MagicMock()
    user.role.codename = user_role
    user.permissions = [MagicMock(codename=perm) for perm in user_permissions]
    user.role.permissions = []

    # Call the method and assert results
    if expected_exception:
        with pytest.raises(expected_exception):
            await auth_manager.check_access(user, roles, permissions)
    else:
        result = await auth_manager.check_access(user, roles, permissions)
        assert result == user

    with pytest.raises(NotImplementedError):
        auth_manager.rp_repo = None
        await auth_manager.check_access(user, roles, permissions)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "email, username, existing_user, user_login_fields, role_id, safe, expected_exception",
    [
        # Case: User already exists by email
        (
            "existing@example.com",
            None,
            True,
            ["email"],
            None,
            True,
            exceptions.UserAlreadyExists,
        ),
        # Case: User already exists by username
        (
            None,
            "existing_user",
            True,
            ["username"],
            None,
            True,
            exceptions.UserAlreadyExists,
        ),
        # Case: User exists by custom fields
        (
            None,
            None,
            True,
            ["username"],
            None,
            True,
            exceptions.UserAlreadyExists,
        ),
        (
            None,
            None,
            True,
            "username",
            None,
            True,
            exceptions.UserAlreadyExists,
        ),
        # Case: Invalid role ID
        (
            None,
            "new_user",
            False,
            ["username"],
            999,
            False,
            exceptions.RoleNotFound,
        ),  # Assuming ValueError for invalid role
        # Case: Successful registration
        (
            "new@example.com",
            "new_user",
            False,
            ["email", "username"],
            None,
            True,
            None,
        ),
    ],
)
async def test_register(
    email,
    username,
    existing_user,
    user_login_fields,
    role_id,
    safe,
    expected_exception,
    auth_manager,
):
    # Mock configuration and dependencies

    auth_manager.password_helper = MagicMock()
    auth_manager._config.USER_LOGIN_FIELDS = user_login_fields
    auth_manager._config.USER_DEFAULT_IS_ACTIVE = True
    auth_manager._config.USER_DEFAULT_IS_VERIFIED = False
    auth_manager._config.USER_DEFAULT_ROLE = "default_role"

    # Setup mocks for user existence and roles
    auth_manager.user_repo.get_by_field.return_value = (
        MagicMock() if existing_user else None
    )
    auth_manager.user_repo.get_by_email.return_value = (
        MagicMock() if existing_user and email else None
    )
    auth_manager.user_repo.get_by_username.return_value = (
        MagicMock() if existing_user and username else None
    )

    auth_manager.user_repo.create.side_effect = lambda data: MagicMock(**data)

    auth_manager.rp_repo.get_role_by_codename.return_value = MagicMock(id=2)
    auth_manager.rp_repo.get_role.return_value = (
        None if role_id == 999 else MagicMock(id=role_id)
    )

    # Mock input data
    data = MagicMock()
    data.model_fields = {}
    if email:
        data.model_fields["email"] = email
    if username:
        data.model_fields["username"] = username
    if isinstance(user_login_fields, list):
        data.model_fields[user_login_fields[0]] = user_login_fields[0]
    else:
        data.model_fields[user_login_fields] = user_login_fields

    if role_id:
        data.model_fields["role_id"] = role_id
    data.model_dump.return_value = {
        "password": "password123",
        "role_id": role_id or None,
    }

    # Call the method and assert outcomes
    if expected_exception:
        with pytest.raises(expected_exception):
            await auth_manager.register(data, safe)
    else:
        result = await auth_manager.register(data, safe)
        assert result is not None

        # test_instance.on_after_register.assert_called_once_with(result, None)

        if role_id:
            assert result.role_id == role_id

            auth_manager.rp_repo.create_role.assert_called_once()


@pytest.mark.parametrize(
    "user, expected_exception",
    [
        (None, exceptions.UserNotFound),
        (MagicMock(is_active=False), exceptions.UserNotFound),
        (MagicMock(id=1, hashed_password="password", is_active=True), None),
    ],
)
@pytest.mark.asyncio
async def test_forgot_password(user, expected_exception, auth_manager):
    auth_manager.user_repo.get_by_email.return_value = user
    auth_manager.token_encoder = MagicMock(spec=TokenHelperProtocol)
    auth_manager.token_encoder.encode_token.side_effect = (
        lambda p, token_type, **kwargs: p
    )
    auth_manager.password_helper = MagicMock(spec=PasswordHelperProtocol)
    auth_manager.password_helper.hash.side_effect = lambda password: password

    if expected_exception:
        with pytest.raises(expected_exception):
            await auth_manager.forgot_password("email")
    else:
        result = await auth_manager.forgot_password("email")
        assert result["sub"] == str(user.id)
        assert result["password_fgpt"] == user.hashed_password


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token, decoded_data, user, valid_fingerprint, update_error, expected_exception",
    [
        # Case: Valid token and successful password reset
        (
            "valid_token",
            {"sub": "user_id_1", "password_fgpt": "valid_fgpt"},
            MagicMock(hashed_password="hashed_pw"),
            True,
            False,
            None,
        ),
        # Case: Invalid token decoding
        ("invalid_token", None, None, False, False, exceptions.InvalidToken),
        # Case: Missing required fields in decoded data
        (
            "valid_token",
            {"password_fgpt": "valid_fgpt"},
            None,
            False,
            False,
            exceptions.InvalidToken,
        ),
        # Case: User not found
        (
            "valid_token",
            {"sub": "user_id_1", "password_fgpt": "valid_fgpt"},
            None,
            False,
            False,
            exceptions.UserNotFound,
        ),
        # Case: Invalid password fingerprint
        (
            "valid_token",
            {"sub": "user_id_1", "password_fgpt": "invalid_fgpt"},
            MagicMock(hashed_password="hashed_pw"),
            False,
            False,
            exceptions.InvalidToken,
        ),
        # Case: Error during user update
        (
            "valid_token",
            {"sub": "user_id_1", "password_fgpt": "valid_fgpt"},
            MagicMock(hashed_password="hashed_pw"),
            True,
            True,
            RuntimeError,  # Assuming a generic error for demonstration
        ),
    ],
)
async def test_reset_password(
    token,
    decoded_data,
    user,
    valid_fingerprint,
    update_error,
    expected_exception,
    auth_manager,
):

    auth_manager.token_encoder = MagicMock()
    auth_manager.password_helper = MagicMock()
    auth_manager._config.JWT_DEFAULT_RESET_AUDIENCE = "reset_audience"

    # Mock token decoding
    if decoded_data is None:
        auth_manager.token_encoder.decode_token.side_effect = PyJWTError(
            "Invalid token"
        )
    else:
        auth_manager.token_encoder.decode_token.return_value = decoded_data

    # Mock user fetching
    auth_manager.user_repo.get_by_id.return_value = user

    # Mock password fingerprint verification
    auth_manager.password_helper.verify_and_update.return_value = (
        valid_fingerprint,
        None,
    )

    # Mock user update
    if update_error:
        auth_manager.user_repo.update.side_effect = RuntimeError("Update error")
    else:
        auth_manager.user_repo.update.return_value = MagicMock()

    # Call the method and assert outcomes
    if expected_exception:
        with pytest.raises(expected_exception):
            await auth_manager.reset_password(token, "new_password")
    else:
        updated_user = await auth_manager.reset_password(token, "new_password")
        assert updated_user is not None


@pytest.mark.parametrize(
    "user, expected_exception",
    [
        (None, exceptions.UserNotFound),
        (MagicMock(is_active=False), exceptions.UserNotFound),
        (MagicMock(is_verified=True), exceptions.HTTPException),
        (MagicMock(id=1, is_verified=False, is_active=True, email="email"), None),
    ],
)
@pytest.mark.asyncio
async def test_request_verify(user, expected_exception, auth_manager):
    auth_manager.user_repo.get_by_email.return_value = user
    auth_manager.token_encoder = MagicMock(spec=TokenHelperProtocol)
    auth_manager.token_encoder.encode_token.side_effect = (
        lambda p, token_type, **kwargs: p
    )
    auth_manager.password_helper = MagicMock(spec=PasswordHelperProtocol)
    auth_manager.password_helper.hash.side_effect = lambda password: password

    if expected_exception:
        with pytest.raises(expected_exception):
            await auth_manager.request_verify("email")
    else:
        result = await auth_manager.request_verify("email")
        assert result["sub"] == str(user.id)
        assert result["email"] == user.email


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token, decoded_data, user, is_verified, update_error, expected_exception",
    [
        # Case: Valid token and successful verification
        (
            "valid_token",
            {"sub": "user_id_1", "email": "user@example.com"},
            MagicMock(is_verified=False, email="user@example.com", id="user_id_1"),
            False,
            False,
            None,
        ),
        # Case: Invalid token decoding
        (
            "invalid_token",
            None,
            None,
            False,
            False,
            exceptions.InvalidToken,
        ),
        # Case: Missing fields in decoded token
        (
            "valid_token",
            {"sub": "user_id_1"},
            None,
            False,
            False,
            exceptions.InvalidToken,
        ),
        # Case: User not found
        (
            "valid_token",
            {"sub": "user_id_1", "email": "user@example.com"},
            None,
            False,
            False,
            exceptions.InvalidToken,
        ),
        # Case: Mismatched user ID
        (
            "valid_token",
            {"sub": "user_id_1", "email": "user@example.com"},
            MagicMock(is_verified=False, email="user@example.com", id="user_id_2"),
            False,
            False,
            exceptions.InvalidToken,
        ),
        # Case: User already verified
        (
            "valid_token",
            {"sub": "user_id_1", "email": "user@example.com"},
            MagicMock(is_verified=True, email="user@example.com", id="user_id_1"),
            True,
            False,
            exceptions.HTTPException,
        ),
        # Case: Error during user update
        (
            "valid_token",
            {"sub": "user_id_1", "email": "user@example.com"},
            MagicMock(is_verified=False, email="user@example.com", id="user_id_1"),
            False,
            True,
            RuntimeError,
        ),
    ],
)
async def test_verify(
    token,
    decoded_data,
    user,
    is_verified,
    update_error,
    expected_exception,
    auth_manager,
):

    auth_manager.token_encoder = MagicMock()
    # auth_manager.parse_id = Mock(side_effect=lambda x: x)
    auth_manager._update_user = AsyncMock()

    # Mock token decoding
    if decoded_data is None:
        auth_manager.token_encoder.decode_token.side_effect = PyJWTError(
            "Invalid token"
        )
    else:
        auth_manager.token_encoder.decode_token.return_value = decoded_data

    # Mock user retrieval
    auth_manager.user_repo.get_by_email.return_value = user

    # Mock user update
    if update_error:
        auth_manager._update_user.side_effect = RuntimeError("Update error")
    else:
        auth_manager._update_user.return_value = MagicMock(is_verified=True)

    # Call the method and assert outcomes
    if expected_exception:
        with pytest.raises(expected_exception):
            await auth_manager.verify(token)
    else:
        verified_user = await auth_manager.verify(token)
        assert verified_user is not None


@pytest.mark.asyncio
async def test_oauth_login(auth_manager):

    strategy = AsyncMock()
    strategy.write_token.side_effect = lambda user, type: f"{user}_{type}"

    with patch("fastauth.manager.get_login_response") as response:
        response.side_effect = lambda security, tokens: tokens

        result = await auth_manager.oauth_login("user", strategy, auth_manager)
        assert isinstance(result, TokenResponse)
        assert result.access_token == f"user_access"
        assert result.refresh_token == f"user_refresh"
