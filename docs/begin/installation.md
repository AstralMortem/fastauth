# Installation

You can add **FastAuth** to your FastAPI project in a few easy steps. First of all, install dependency:

To install default dependency over pip:
```
pip install fastapi-fastauth
```
When you install fastauth simply, you will have only authentication dependencies installed. It`s highly recommended to install ORM,
for RBAC and User management support. FastAuth support some popular ORM implementations, if you dont see suitable ORM, you can
implement your own support, see:


### ORM Support
To enable ORM support**(Recommended)**
=== "SQLAlchemy"
```
pip install "fastapi-fastauth[sqlalchemy]"
```

### OAuth2 Support
To enable OAuth2 support use:
```
pip install "fastapi-fastauth[oauth]"
```
