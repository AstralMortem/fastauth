from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from fastauth.contrib.sqlalchemy import models


class Model(DeclarativeBase):
    pass


class User(models.SQLAlchemyBaseUserUUID, Model):
    pass


class User(models.SQLAlchemyBaseUser[int], Model):
    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
