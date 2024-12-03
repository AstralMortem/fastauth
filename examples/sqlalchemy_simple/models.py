from examples.db import Model
from fastauth.contrib.sqlalchemy.models import (
    SQLAlchemyUserUUID,
)


class User(SQLAlchemyUserUUID, Model):
    pass
