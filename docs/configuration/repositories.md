# Repositories

Repository pattern is a way to abstract the data layer from the business logic layer.
It is a way to organize your code in a way that makes it easier support for different ORM system.
In this section, we will learn how to create repositories for our models.


## Interfaces

To create a repository, we need to implement the repositories interface, which located in `fastauth.repositories` module.
FastAuth provides a 3 base interfaces: `AbstractUserRepository`, `AbstractRolePermissionRepository`, and `AbstractOAuthRepository`.

!!! tip "Repository interfaces"
    === "AbstractUserRepository"
        ```python
        --8<-- "fastauth/repositories.py:9:86"
        ```

    === "AbstractRolePermissionRepository"
        ```python

        --8<-- "fastauth/repositories.py:89:200"
        ```
    === "AbstractOAuthRepository"
        ```python
        --8<-- "fastauth/repositories.py:203"
        ```

## Implementation

FastAuth provides already implemented repositories for supported ORMs.

* [SQLAlchemy](/contrib/sqlalchemy/repositories)

If you don't see your ORM in the list, you can implement your own repository by implementing the repository interface.
To implement a repository, you need to create a class that inherits repositories implementation for specified ORMs, which
located in `fastauth.contrib.<ORM>.repositories` module.

You need pass model class to repository Generic for type hinting, and also set class attribute with suffix `model` to the model class.
For UserRepository, set `user_model`, for RBACRepository set `role_model` and `permission_model`, and for OAuthRepository set `user_model` and `oauth_model`.
See example below:

!!! example "SQLAlchemy Repository implementation"
    ```python
    --8<-- "docs/snippets/sqlalchemy/repositories.py"
    ```
