# Token strategy

To make library more flexible, and independent from any specific token type(JWT, Session, Redis, etc.), it uses `TokenStrategy` class.
`TokenStrategy` is a class responsible for token decoding, and encoding.

```python
--8<-- "fastauth/strategy/base.py:9:14"
--8<-- "fastauth/strategy/base.py:21:24"
--8<-- "fastauth/strategy/base.py:32:33"
```

It has 2 methods: `read_token` and `write_token`, which are responsible for decoding and encoding token respectively.
`read_token` method take token string decoding it and return token data dict.
`write_token` method take `User` model and `TokenType`, decoding it and return token string.

FastAuth supports most popular token strategies:

- [JWT](https://jwt.io/introduction)
- [Redis](https://redis.io/)
- Database

You can create your own strategy, just implement `TokenStrategy` class interface.

## JWTStrategy

[JWTStrategy](#) is a class responsible for JWT token decoding, and encoding. It uses `pyjwt` library under the hood.

!!! note "JWTStrategy implementation"
    ```python
    --8<-- "fastauth/strategy/jwt.py"
    ```

## RedisStrategy

**Not implemented yet**

## DatabaseStrategy

**Not implemented yet**

## Dependency

You can create dependency callable for token strategy to use it later. First argument of callable should be `FastAuthConfig` instance.
We use DI, because strategy can use some dependencies, like `Redis` connection, `Database` connection, etc.
For `JWTStrategy` it looks like this:

```python
from fastauth.strategy import JWTStrategy
from fastauth.config import FastAuthConfig

async def get_strategy(config: FastAuthConfig, **kwargs):
    return JWTStrategy(config)

```
