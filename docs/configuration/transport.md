from fastauth.transport import TokenTransport

# Token transport

The token transport is class which is responsible for creating login and logout responses, and token schema validation.
It takes `FastAuthConfig.TOKEN_LOCATIONS` argument and try to get token from provided locations.

```python
--8<-- "fastauth/transport/base.py:14"
```

FastAuth provide 4 token locations:

* headers - [BearerTransport](#)
* cookies - [CookieTransport](#)
* query - [QueryTransport](#)
* body - [BodyTransport](#)

This class stored in TRANSPORT_GETTER dict in `fastauth.transport` module.
To get token from response it user `fastauth.transport.get_token_from_request` function, which iterate through provided `SecurityBase` classes.
If at least one token found it return token string, else it raises `MissingToken` exception.

```python
--8<-- "fastauth/transport/__init__.py:17:71"
```

To get login or logout response user `get_login_response` and `get_logout_response` from `fastauth.transport` module respectively.

```python
--8<-- "fastauth/transport/__init__.py:74"
```

If you want to customize or create own Transport, just implement `fastauth.transport.base.TokenTransport` class, and overrides `TRANSPORT_GETTER` dict

```python
from fastauth.transport.base import TokenTransport
from fastauth import transport

class MyTransport(TokenTransport):
    ...

transport.TRANSPORT_GETTER["headers"] = MyTransport

```

If you use custom Transport name, don`t forget to set it in FastAuthConfig.TOKEN_LOCATIONS list.
