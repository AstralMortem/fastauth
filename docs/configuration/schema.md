# Schemas

Before sending ORM models to client, we need to validate and serialize them. This is done by using a `pydantic v2`
library. All schemas are located in `fastauth.schema` module.

## User schema

For CRUD operations we need to inherit `BaseUserRead`, `BaseUserCreate` and `BaseUserUpdate` schemas, and expand them
with fields accordingly to our ORM model. For read schema we need pass ID Type as in our ORM model.

```python
--8<-- "docs/snippets/schema/user.py"
```

## RBAC schemas

### Permission schema

For permission schema we need to inherit `BasePermissionRead`, `BasePermissionCreate` and `BasePermissionUpdate` schemas

```python
--8<-- "docs/snippets/schema/rbac.py:1:25"
```

### Role schema

For role schema we need to inherit `BaseRoleRead`, `BaseRoleCreate` and `BaseRoleUpdate` schemas. Also we need pass `PermissionRead` class
to Generic type, to bind Role and Permission schema.

```python
--8<-- "docs/snippets/schema/rbac.py:1:12"

--8<-- "docs/snippets/schema/rbac.py:26:36"
```

### RBAC Mixin

To bind User with Roles and Permission we need to extend user create and read schemas with `RBACMixin` class. And pass `RoleRead` and `PermissionRead` classes to Generic type.

```python hl_lines="14 18"
--8<-- "docs/snippets/schema/rbac.py:1:12"

--8<-- "docs/snippets/schema/rbac.py:39:45"
```

## OAuth schemas

### OAuthAccount schema

We need create only read schema for OAuthAccount model. Inherit `BaseOAuthAccountRead` and pass ID field type to Generic.

```python
--8<-- "docs/snippets/schema/oauth.py::6"
```

### OAuthMixin

To bind User with OAuthAccount we need to extend `UserRead` with `OAuthMixin` class. And pass `OAuthAccountRead` class to Generic type.

```python hl_lines="9"
--8<-- "docs/snippets/schema/oauth.py"
```

## Full User Schema

To get full featured User schema we need to inherit all mixins and pass all Generic types.

```python hl_lines="6-7 9-10"
from fastauth.schema import BaseUserRead, BaseUserCreate, RBACMixin, BaseUserUpdate
import uuid

...

class UserRead(BaseUserRead[uuid.UUID], RBACMixin[RoleRead, PermissionRead], OAuthMixin[OAuthAccountRead]):
    pass

class UserCreate(BaseUserCreate, RBACMixin):
    pass

class UserUpdate(BaseUserUpdate):
    pass

...

```
