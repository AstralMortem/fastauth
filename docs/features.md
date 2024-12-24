from requests import session

# FastAuth Feature

## Full example for SQLAlchemy and JWTStrategy

=== "models.py"
    ```python
    --8<-- "docs/snippets/sqlalchemy/models/full.py"
    ```
=== "schema.py"
    ```python
    --8<-- "docs/snippets/schema/full.py"
    ```
=== "repositories.py"
    ```python
    from .models import User, Role, Permission, OAuthAccount
    --8<-- "docs/snippets/sqlalchemy/repositories.py"
    ```
=== "db.py"
    ```python
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
    engine = create_async_engine("DATABASE_URL")
    sessionmaker = async_sessionmaker(engine)

    async def get_db() -> AsyncSession:
        session = sessionmaker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
    ```

=== "manager.py"
    ```python
    from .models import User, Role, Permission, OAuthAccount
    from .repositories import UserRepository, RBACRepository, OAuthRepository
    from .db import get_db, AsyncSession
    --8<-- "docs/snippets/manager.py::27"
    ```

=== "dependencies.py"
    ```python
    from .manager import get_auth_manager
    from fastauth import FastAuth, FastAuthConfig
    from fastauth.strategy import JWTStrategy

    config = FastAuthConfig()

    security = FastAuth(config, get_auth_manager)

    # You can also separate `token_strategy` method and set as FastAuth(config, get_auth_manager, token_strategy)
    @security.set_token_strategy
    async def token_strategy(config: FastAuthConfig, **kwargs):
        return JWTStrategy(config)
    ```
## Dependencies

FastAuth class provides 3 base dependencies methods `access_token_required`, `refresh_token_required`, and `user_required`

### Tokens Required

If you want to get decoded token payload dict, of specific type, you can use `access_token_required` and `refresh_token_required` dependency.
Pass it to Depends() function in router

```python
from .dependencies import security
from fastapi import FastAPI, Depends
from typing import Any

app = FastAPI()

@app.get('/protected')
async def get_access_token(token: dict[str, Any] = Depends(security.access_token_required())):
    return token

@app.get('/refresh')
async def get_refresh_token(token: dict[str, Any] = Depends(security.refresh_token_required())):
    return token
```

### User required

To get authenticated User model, you can use `user_required` dependency.

```python
from .dependencies import security
from fastapi import FastAPI, Depends
from .schema import UserRead

app = FastAPI()

@app.get('/users/me', response_model=UserRead)
async def get_me(user = Depends(security.user_required())):
    return user

```

You can set `is_active` or `is_verified` flag to allow access for unactive or unverified users.
You can define global property in `FastAuthConfig.USER_DEFAULT_IS_ACTIVE` and `FastAuthConfig.USER_DEFAULT_IS_VERIFIED`.

```python hl_lines="3"
# Allow access to route for only active and verified and unverified user
@app.get('/users/me', response_model=UserRead)
async def get_me(user = Depends(security.user_required(is_active=True, is_verified=False))):
    return user
```

#### RBAC Support

If you set RBACRepository into AuthManager, you now can protect routes, by setting allowed access for user with sepcified
role or permissions. You can just set role codename in `roles` args, and permission codename in `permissions` args

```python
# Allow access only for user with role.codename == User
@app.get('/users/me', response_model=UserRead)
async def get_me(user = Depends(security.user_required(roles=["User"]))):
    return user

# Allow access only for user with role.codename == Admin,
# or permissions.codename == user:delete
# or role.permissions.codename == user:delete, etc.
@app.delete("/users/{id}")
async def delete_user(
    id: uuid.UUID,
    user=Depends(
        security.user_required(
            roles=["Amdin"],
            permissions=["user:delete"],
        )
    ),
):
    return None

```

## Dependency Aliases

For fast development FastAuth provides Dependency Aliases, its already defined FastAPI Depends as property

### Tokens aliases

For access and refresh token requirement, you can use `ACCESS_TOKEN`, `REFRESH_TOKEN` property.

```python
from .dependencies import security
from fastapi import FastAPI

app = FastAPI()
@app.get('/protected')
async def token(token: dict = security.ACCESS_TOKEN):
    return token

```

### Users

FastAuth provides 2 users Alias:

* `DEFAULT_USER` - with defined `roles`, `is_active`, `is_verified` from FastAuthConfig `USER_DEFAULT_ROLE`, `USER_DEFAULT_IS_ACTIVE`, `USER_DEFAULT_IS_VERIFIED`
* `ADMIN_REQUIRED` - with defined `roles`, `is_active`, `is_verified` from FastAuthConfig `ADMIN_DEFAULT_ROLE`, `USER_DEFAULT_IS_ACTIVE`, `USER_DEFAULT_IS_VERIFIED`

```python
from .dependencies import security
from fastapi import FastAPI
from .schema import UserRead

app = FastAPI()
@app.get('/users/me', response_model=UserRead)
async def token(user = security.DEFAULT_USER):
    return user

```

### Callbacks

To get BaseAuthManager instance dependency you can use `AUTH_MANAGER` property.

```python
from .dependencies import security
from fastapi import FastAPI
import uuid

app = FastAPI()
@app.delete('/users/{id}', dependencies=[security.ADMIN_REQUIRED])
async def token(id: uuid.UUID, manager = security.AUTH_MANAGER):
    return await manager.delete_user(id)

```

If you need to get TokenStrategy instance as FastAPI Dependency, you can use `TOKEN_STRATEGY` property.

```python
from .dependencies import security
from fastapi import FastAPI

app = FastAPI()
@app.post('/login')
async def token(username: str, password: str, strategy = security.TOKEN_STRATEGY):
    payload = {
        "username": username,
        "password": password
    }
    return await strategy.write_token(payload, "access")
```


## Tools

### Token creation

You can create access or refresh tokens from FastAuth instance.

```python
from .dependencies import security

access_token = security.create_access_token(
    uid="1", # User ID
    max_age=3600, # Access token max age, in JWT 'exp' field
    # Extra fields in token payload, if you want to add fields from user model,
    # just add field name in FastAuthConfig.USER_FIELDS_IN_TOKEN list attribute
    extra={
        "is_active": True
    }
)

refresh_token = security.create_refresh_token(
    uid="1",
    max_age=3600
)

```

### Cookie

You can set access or refresh cookie manually from FastAuth instance.

```python
from .dependencies import security
from fastauth import Response

access_token = security.create_access_token(
    uid="1",
    max_age=3600,
    extra={
        "is_active": True
    }
)

refresh_token = security.create_refresh_token(
    uid="1",
    max_age=3600
)

response = Response()
# Set access cookie, if you want to modify cookie max age, name, etc. look in COOKIE section
# in FastAuthConfig class.
response = security.set_access_cookie(access_token, response)

# Set refresh cookie
response = security.set_refresh_cookie(refresh_token, response)

# Remove all cookies, access and refresh
response = security.remove_cookies(response)

```
