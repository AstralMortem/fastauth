# SQLAlchemy repositories

Repositories are used to interact with the database and perform CRUD operations.
All SQLAlchemy repositories are located in the `fastauth.contrib.sqlalchemy.repositories` module.
All repository have a `AsyncSession` in __init__ method, to run db operations.

## User repository

The user repository is used to interact with the `User` model in the database.
To create user repository inherit `SQLAlchemyUserRepository` class and set the `user_model` attribute.
Also set User and ID type in Generic to get type hinting.

```python
--8<-- "docs/snippets/sqlalchemy/repositories.py::7"
```

## RBAC repository

The RBAC repository is used to interact with the `Role` and `Permission` models.

```python
--8<-- "docs/snippets/sqlalchemy/repositories.py::3"


--8<-- "docs/snippets/sqlalchemy/repositories.py:10:12"
```

## OAuth repository

The OAuth repository is used to interact with the `OAuth` and `User` models.

```python
--8<-- "docs/snippets/sqlalchemy/repositories.py::3"


--8<-- "docs/snippets/sqlalchemy/repositories.py:15:17"
```

## Full example

```python
--8<-- "docs/snippets/sqlalchemy/repositories.py"
```
