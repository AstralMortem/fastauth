# FastAuth
<p align="center">
  <img src="https://raw.githubusercontent.com/AstralMortem/fastauth/master/logo.png?sanitize=true" alt="FastAuth">
</p>

<p align="center">
    <em>Ready-to-use customizable solution for FastAPI with Authentication, Authorization(RBAC) and OAuth2 support</em>
</p>

---
## About

[![CI](https://github.com/AstralMortem/fastauth/actions/workflows/ci.yaml/badge.svg)](https://github.com/AstralMortem/fastauth/actions/workflows/ci.yaml)
[![MkDocs](https://github.com/AstralMortem/fastauth/actions/workflows/docs.yaml/badge.svg)](https://github.com/AstralMortem/fastauth/actions/workflows/docs.yaml)


Here’s a ready-to-use, customizable solution for FastAPI with Authentication, Authorization (RBAC), and OAuth2 support. 
This solution provides token based authentication(JWT, Redis, DB), role-based access control, and OAuth2 integration.
Highly inspired by [FastAPI Users](https://github.com/fastapi-users/fastapi-users) and [AuthX](https://github.com/yezz123/authx/tree/main):

* **Documentation**: <https://astralmortem.github.io/fastauth/>
* **Source Code**: <https://github.com/AstralMortem/fastauth>
---

## Features

* [x] Authentication Support:
    * [x] Access and Refresh Token Dependencies
    * [x] Different Token Strategy(JWT, Redis, Session)
    * [x] Different Token locations(Header, Cookie, Query, etc.)
* [x] Authorization Support:
    * [x] "Role and Permission required" Dependency
    * [x] OAuth2 support
* [x] User Management:
    * [x] User Model protocol
    * [x] Service-Repository pattern for flexible customization
    * [ ] Popular ORM support:
        * [ ] SQLAlchemy2.0 support
        * [ ] Beanie
        * [ ] Tortoise ORM
