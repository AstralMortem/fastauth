# Models

FastAuth models is compatible with various **databases and ORM**. FastAuth provide ready-to-use ORM Models mixins which
you can find in ``fastauth.contrib.<ORM>.models`` module. For now fastauth supports the following ORM models:

* [SQLAlchemy](/contrib/sqlalchemy/models)

---
Every model just follow convention, so if you need add own ORM model, you need just follow this 4 protocols:

 * [UserProtocol](/api/models/#fastauth.models.UserProtocol) - User model protocol
 * [RoleProtocol](/api/models/#fastauth.models.RoleProtocol) - Role model protocol
 * [PermissionProtocol](/api/models/#fastauth.models.PermissionProtocol) - Permission model protocol
 * [OAuthProtocol](/api/models/#fastauth.models.OAuthProtocol) - OAuth model protocol
