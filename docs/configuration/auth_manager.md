# Auth Manager

The `BaseAuthManager` is responsible for managing authentication, authorization, and ORM models management.
This is layer between client and Database. It uses Repositories to interact with the database.

## Creation

To create AuthManager, simply inherit `BaseAuthManager` from `fastauth.manager` module.
After inhering we need to override `parse_id(self, pk: str)` method. This method is used to convert user primary key
from string(which we get from client or token) to the type stored in ORM model.
We can pass ORM models to the `BaseAuthManager` Generic for type hinting.

```python
--8<-- "docs/snippets/manager.py::9"
```

Also we use AuthManager to override event methods like `on_after_login`, `on_after_register` etc. Supported events are:



```python
--8<-- "docs/snippets/manager.py::15"
```

!!! tip "Supported events"
    - `on_after_login` - called when user logged in. Provide User model and Request

## Dependency

We can define dependency callable for AuthManager, to passed it in `FastAuth` class. The main differeces from other dependencies callable,
is than callable take `FastAuthConfig` instance as first argument.
So if we use SQLAlchemy ORM, we need to create Repositories which need `AsyncSession` dependency, and pass it to AuthManager:

```python
--8<-- "docs/snippets/manager.py:16:29"
```

Auth manager also get password helper and token encoder instances, which can be passed to `__init__` method.

```python hl_lines="10"
--8<-- "docs/snippets/manager.py:30:"
```

### Password Helper

Password helper is used to hash and verify passwords. It should implement `PasswordHelperProtocol` from `fastauth.utils.password` module.
By default `BaseAuthManager` uses `PasswordHelper` class, which uses `argon2` and `bcrypt` hashing algorithms, provided by `pwdlib` package

```python
--8<-- "fastauth/utils/password.py:9:16"
```

!!! tip "PasswordHelper"
    ```python
    --8<-- "fastauth/utils/password.py:18"
    ```

### Token Encoder

Token encoder is used to encode and decode tokens, as well as `TokenStrategy` but on lower level. It should implement `TokenEncoderProtocol` from `fastauth.utils.jwt_helper` module.
By default it use `JWT` class from `fastauth.utils.jwt_helper` module.

```python
--8<-- "fastauth/utils/jwt_helper.py:9:16"
```

!!! tip "JWT helper class"
    ```python
    --8<-- "fastauth/utils/jwt_helper.py:18"
    ```
