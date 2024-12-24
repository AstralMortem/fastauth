# FastAuth Routers

FastAuth provides predefined routers with deep integration with swagger. To use it in you app, init `FastAuthRouter` class
from `fastauth.routers` module with `FastAuth` instance, and then simply add it to your `FastAPI` routers.

```python
from .dependencies import security
from fastauth.routers import FastAuthRouter
from fastapi import FastAPI
app = FastAPI()

auth_router = FastAuthRouter(security)
```

## Auth router
To add such routes as `/auth/token/login`, `/auth/refresh`, `/auth/logout` user `get_auth_router` method. If you want, you
can customize prefixes and routes inside FastAuthConfig ROUTER section
```python

app.include_router(
    auth_router.get_auth_router(),
    tags=["Auth"]
)

```

## Register router
To add `/auth/register` route, use `get_register_router` method

```python
from .schema import UserRead, UserCreate

app.include_router(
    auth_router.get_register_router(UserRead, UserCreate),
    tags=["Auth"]
)
```

## Users router
To add `/users` crud routers, user, `get_users_router` method

```python
from .schema import UserRead, UserUpdate

app.include_router(
    auth_router.get_users_router(UserRead, UserUpdate),
    tags=["Users"]
)
```

## Roles router
By default roles router user ADMIN_DEFAULT_ROLE, USER_DEFAULT_IS_ACTIVE, USER_DEFAULT_IS_VERIFIED,
but you can manually pass it for routers by `default_admin_role`, `is_active`, `is_verified` args.

```python
from .schema import RoleRead, RoleCreate, RoleUpdate

app.include_router(
    auth_router.get_roles_router(RoleRead, RoleCreate, RoleUpdate),
    tags=["Roles"]
)
```

## Permissions router
By default roles router user ADMIN_DEFAULT_ROLE, USER_DEFAULT_IS_ACTIVE, USER_DEFAULT_IS_VERIFIED,
but you can manually pass it for routers by `default_admin_role`, `is_active`, `is_verified` args.

```python
from .schema import PermissionRead, PermissionCreate, PermissionUpdate

app.include_router(
    auth_router.get_permissions_router(PermissionRead, PermissionCreate, PermissionUpdate),
    tags=["Roles"]
)
```

## Verification router
```python
from .schema import UserRead

app.include_router(
    auth_router.get_verify_router(UserRead),
    tags=["Auth"]
)
```

## Reset password router
```python
app.include_router(
    auth_router.get_reset_router(),
    tags=["Auth"]
)
```

## OAuth router
To get oauth router you need to setup OAuth client, and pass it to router. If you also have RBAC support, you need to set True
in `default_role`, or role codename if you don`t want to use FastAuthConfig.USER_DEFAULT_ROLE

```python
from .oauth import github_client

app.include_router(
    auth_router.get_oauth_router(github_client, default_role=True),
    tags=["OAuth"]
)
```

## In Hurry?
If you want to fast test all routers(except OAuth), you can use `register_in_fastapi` method, set app instance, and pydantic models
```python
from fastapi import FastAPI
from fastauth.routers import FastAuthRouter
from .dependencies import security
from .schema import *

app = FastAPI()
auth_router = FastAuthRouter(security)

ROUTER_SCHEMA = {
    "user": {
        "read": UserRead,
        "create": UserCreate,
        "update": UserUpdate,
        "is_active": True,
        "is_verified": False,
    },
    "role": {
        "read": RoleRead,
        "create": RoleCreate,
        "update": RoleUpdate,
    },
    "permission": {
        "read": PermissionRead,
        "create": PermissionCreate,
        "update": PermissionUpdate,
    },
}

auth_router.register_in_fastapi(app,ROUTER_SCHEMA)


```
