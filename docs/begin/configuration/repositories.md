# Repositories

After creating models, you need to create Repositories. Repository is just ORM adapter which execute queries by AuthManager.
FastAuth provide only 3 repository protocol:

* [User repository](/api/repositories/#fastauth.repository.UserRepositoryProtocol) - to do actions with User model (adds UserManagement features)
* [RBAC repository](/api/repositories/#fastauth.repository.RolePermissionRepositoryProtocol) - to do actions with Role and Permission model (adds RBAC features)
* [OAuth repository](/api/repositories/#fastauth.repository.OAuthProtocol) - to do actions with OAuthAccount model (adds OAuth2 features)
---
To create Repository just create class and inherit repository mixin for your ORM ```fastauth.contrib.<ORM>.repository```
and pass your model to class variable `model`

* [SQLAlchemy](/contrib/sqlalchemy/repositories)