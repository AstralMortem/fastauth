# Installation

You can add **FastAuth** to your FastAPI project in a few easy steps. First of all, install dependency:

To install default dependency over pip:
```
pip install fastapi-fastauth
```
When you install fastauth simply, you will have only authentication dependencies installed. It's highly recommended to install ORM,
for RBAC and User management support. FastAuth support some popular ORM implementations, if you don't see suitable ORM, you can
implement your own support, see:

[Extra](/)

### ORM Support
To enable ORM support**(Recommended)**, install the following extra dependency:
=== "SQLAlchemy"
```
pip install "fastapi-fastauth[sqlalchemy]"
```

### OAuth2 Support
To add OAuth2 support install following extra dependency:
```
pip install "fastapi-fastauth[oauth]"
```
