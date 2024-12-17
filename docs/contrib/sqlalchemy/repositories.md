# SQLAlchemy repositories

After creation models, we need to create `Repositories` for all models
## User Repository

```python
from fastauth.contrib.sqlalchemy import SQLAlchemyUserRepository
import uuid
import User # from previous examples

class UserRepository(SQLAlchemyUserRepository[User, uuid.UUID]):
    user_model = User

```

And it's all, if you need you can override default sqlalchemy orm queries, or add your own, and then override
`BaseAuthManager` to call it in routes.

## RBAC Repository

```python
from fastauth.contrib.sqlalchemy import SQLAlchemyRBACRepository
import Role, Permission # from previous examples

class RBACRepository(SQLAlchemyRBACRepository[Role, Permission])
    role_model = Role
    permission_model = Permission
```

## OAuth Repository
```python
from fastauth.contrib.sqlalchemy import SQLAlchemyOAuthRepository
import uuid
import OAuthAccount # from previous examples

class RBACRepository(SQLAlchemyOAuthRepository[OAuthAccount, uuid.UUID]):
    oauth_model = OAuthAccount

```
