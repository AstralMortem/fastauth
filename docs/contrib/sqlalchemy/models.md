# SQLAlchemy Models

All predefined models are located in `fastauth.contrib.sqlalchemy.models` module.

## User model

The User model represents the user data in the database. It is the most important model in the application.
To define simple User model you can use [`SQLAlchemyBaseUserModel`](/api/contrib/sqlalchemy/models) class.

```python
--8<-- "docs/snippets/sqlalchemy/models/simple.py::12"
```

!!! tip "User ID type"
    By default [`SQLAlchemyBaseUserUUID`](/api/contrib/sqlalchemy/models) use `UUID` type as primary key. If you want to use another type, you can inherit
    [`SQLAlchemyBaseUser`](/api/contrib/sqlalchemy/models) class and override `id` field.:
    ```python
    --8<-- "docs/snippets/sqlalchemy/models/simple.py:12:15"
    ```

## Role and Permission models

Role and Permission models are used to define the user roles and permissions. They are used to define the user access rights.
To define simple Role and Permission models you can use [`SQLAlchemyBaseRoleModel`](/api/contrib/sqlalchemy/models) and
[`SQLAlchemyBasePermissionModel`](/api/contrib/sqlalchemy/models) classes.
Also we need create many-to-many relationship between User and Role models and between Role and Permission models.
Inherit [`SQLAlchemyBaseRolePermissionRel`](/api/contrib/sqlalchemy/models) class and set `Mapped` relationship in RoleModel.

```python
--8<-- "docs/snippets/sqlalchemy/models/rbac.py::20"
```

And after that we need to bind our `Role` and `Permission` models with `User` model. FastAuth provide [`UserRBACMixin`](/api/contrib/sqlalchemy/models). User also have many-to-many
relationship with permissions and role. We need to add class with inherited [`SQLAlchemyBaseUserPermissionRel`](/api/contrib/sqlalchemy/models) class

```python hl_lines="23-27 30-31"

--8<-- "docs/snippets/sqlalchemy/models/rbac.py"
```

## OAuth model

OAuth model is used to store the OAuth tokens. It is used to authenticate the user with OAuth providers.
To define simple OAuth model you can use [`SQLAlchemyBaseOAuthAccountUUID`](/api/contrib/sqlalchemy/models) class.

```python
--8<-- "docs/snippets/sqlalchemy/models/oauth.py::12"
```

!!! tip "OAuth ID type"
    By default [`SQLAlchemyBaseOAuthAccountUUID`](/api/contrib/sqlalchemy/models) use `UUID` type as primary key. If you want to use another type, you can inherit
    [`SQLAlchemyBaseOAuthAccount`](/api/contrib/sqlalchemy/models) class and override `id` field.:

    ```python
    --8<-- "docs/snippets/sqlalchemy/models/oauth.py:16:19"
    ```


Then we need to bind our `OAuth` model with `User` model. FastAuth provide [`UserOAuthMixin`](/api/contrib/sqlalchemy/models).

```python hl_lines="13-15"
--8<-- "docs/snippets/sqlalchemy/models/oauth.py"
```

## Full Example

To get full featured User model you can combine all user mixins

```python
--8<-- "docs/snippets/sqlalchemy/models/full.py"
```
