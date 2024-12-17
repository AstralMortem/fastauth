# FastAuth

After creation AuthManager and TokenStrategy, we need to create FastAuth class, which have all required dependencies,
and set Manager and Strategy properties.

```python
from fastauth.fastauth import FastAuth
from fastauth.config import FastAuthConfig
from fastauth.strategy import JWTStrategy

auth_config = FastAuthConfig()
security = FastAuth(auth_config)

@security.set_auth_callback
async def auth_callback(config: FastAuthConfig):
    return AuthManager(
                config,
                UserRepository(), # User repository created erlier 
                RBACRepository(), # Role and permissions repository
                OAuthRepository() # OAuth repository
    )


@security.set_token_strategy
async def token_strategy(config: FastAuthConfig):
    return JWTStrategy(config)

```

!!! note "Why decorators"
    We use `@security.set_token_strategy` and `@security.set_auth_callback` decorator to pass async function which wraps in
    dependency callable, for properly DI, for example, in SQLAlchemy, repositories need AsyncSession instance, then we can pass
    Depends session like that:
    ```python
    @security.set_auth_callback
    async def auth_callback(config: FastAuthConfig, session: AsyncSession = Depends(get_db)):
        return AuthManager(
                    config,
                    UserRepository(session), 
                    RBACRepository(session),
                    OAuthRepository(session))
    ```


After all, our FastAuth instance can be used in routes:

```python
from fastapi import FastAPI, Depends
from fastauth.schema import TokenPayload

app = FastAPI()

@app.get("/protected")
async def protected_route(token: TokenPayload = Depends(security.access_token_required())):
    return token
```

You can see full examples for every supported ORM:

* [SQLAlchemy](/contrib/sqlalchemy/index.md) 