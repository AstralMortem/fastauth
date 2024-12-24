# Models

Models are the core of the application. They are the classes that represent the data in the database.
Every ORM can have its own way of defining models fields, but they all should follow based Protocol.
FastAuth provide predefined User models for most popular ORMs, you can find them in `fastauth.contrib.<ORM>.models` module. Supported ORMs:

* [SQLAlchemy](/contrib/sqlalchemy/models)

## User model

The User model represents the user data in the database. It is the most important model in the application.
Every User model should follow [`UserProtocol`](#)

!!! tip "UserProtocol"
    ```py
    --8<-- "fastauth/models.py:6:12"
    ```

For example SQLAlchemy User model can be defined as:
!!! example "User model"
    ```python
    --8<-- "docs/snippets/sqlalchemy/models/simple.py::12"
    ```
    [See more...](/contrib/sqlalchemy/models#user-model)


## Role and Permission models

Role and Permission models are used to define the user roles and permissions. They are used to define the user access rights.
This models should follow [`RoleProtocol`](#) and [`PermissionProtocol`](#) respectively.

!!! tip "RoleProtocol and PermissionProtocol"
    ```py
    --8<-- "fastauth/models.py:27:30"

    --8<-- "fastauth/models.py:18:21"

    ```

FastAuth also provide predefined Role and Permission models in `fastauth.contrib.<ORM>.models` module.
For example SQLAlchemy Role and Permission models can be defined as:

!!! example "Role and Permission models"
    ```python
    --8<-- "docs/snippets/sqlalchemy/models/rbac.py::20"
    ```
    [See more...](/contrib/sqlalchemy/models##role-and-permission-models)


### Setup RBAC mixins

To bind `RBAC` models with `User` model we need follow expanded protocol [`RBACUserProtocol`](#)
!!! tip "RBACUserProtocol"
    ```py
    --8<-- "fastauth/models.py:36:39"
    ```

As we see, we inherit previous `UserProtocol` and add `roles` and `permissions` fields. So in real case we can create Mixin class for User model:
For example in SQLAlchemy we use `UserRBACMixin` and defines fields and relations:

!!! example "UserRBACMixin"
    ```python hl_lines="23-27 30-31"
    --8<-- "docs/snippets/sqlalchemy/models/rbac.py"
    ```
    [See more...](/contrib/sqlalchemy/models##role-and-permission-models)


## OAuthAccount model

OAuth model is used to store the OAuth tokens. It is used to authenticate the user with OAuth providers.
Every OAuth model should follow [`OAuthAccountProtocol`](#)

!!! tip "OAuthAccountProtocol"
    ```py
    --8<-- "fastauth/models.py:45:52"
    ```

For example SQLAlchemy OAuth model can be defined as:
!!! example "OAuth model"
    ```python
    --8<-- "docs/snippets/sqlalchemy/models/oauth.py::12"
    ```
    [See more...](/contrib/sqlalchemy/models#oauth-model)

### Setup OAuth mixins

To bind `OAuth` model with `User` model we need follow expanded protocol [`OAuthUserProtocol`](#)
!!! tip "OAuthUserProtocol"
    ```py
    --8<-- "fastauth/models.py:58:59"
    ```

We can also create Mixin class for User model. For example in SQLAlchemy we use `UserOAuthMixin` and defines fields and relations:

!!! example "UserOAuthMixin"
    ```python hl_lines="13-15"
    --8<-- "docs/snippets/sqlalchemy/models/oauth.py::15"
    ```
    [See more...](/contrib/sqlalchemy/models#oauth-model)
