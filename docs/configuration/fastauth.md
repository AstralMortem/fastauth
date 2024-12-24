from examples.sqlaclhemy_full.dependency import securityfrom examples.sqlaclhemy_full.dependency import config

# FastAuth

FastAuth is base class which combine AuthManager, TokenStrategy instances and provide methods for creation tokens, and cookies
and dependencies for authentication and authorization.

## FastAuthConfig

Before creating FastAuth instance we need to init FastAuthConfig instance. FastAuthConfig is a class which contains all necessary configurations for FastAuth.
You can override it on your own, or expand it with your own properties.
To see all available properties you can check [FastAuthConfig](#) class in API references.

!!! tip "FastAuthConfig piece of code"
    ```python
    --8<-- "fastauth/config.py:9:30"
        ...
    ```

## Configure

To configure FastAuth you need to create `AuthManager`, `TokenStrategy`, and `FastAuthConfig` instances and pass them to FastAuth constructor.
Also you need set token location: Place where request should get token from. It can be `headers`, `cookies`. Is in FastAuthConfig.TOKEN_LOCATIONS.


```python
from fastauth import FastAuth, FastAuthConfig

config = FastAuthConfig(TOKEN_LOCATIONS=["headers", "cookies"])
security = FastAuth(config,
                    get_auth_manager, # Async callable created in previous parts return AuthManager instance
                    get_token_strategy) # Async callable created in previous parts, return JWStrategy instance
```

Another way you can pass dependencies to FastAuth instance is to use `@set_auth_callback` and `@set_token_strategy` decorators:

```python
from fastauth import FastAuth, FastAuthConfig
from fastauth.strategy import JWTStrategy

config = FastAuthConfig()
security = FastAuth(config)

@security.set_auth_callback
async def auth_callback(config: FastAuthConfig, session: AsyncSession = Depends(get_db)):
    return AuthManager(
        config,
        UserRepository(session)
    )

@security.set_token_strategy
async def token_strategy(config: FastAuthConfig, **kwargs):
    return JWTStrategy(config)

```

Now you have ready to use FastAuth instance with configured AuthManager and TokenStrategy.
