from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from fastauth.contrib.sqlalchemy import models


class Model(DeclarativeBase):
    pass


class OAuthAccount(models.SQLAlchemyBaseOAuthAccountUUID, Model):
    pass


class User(models.SQLAlchemyBaseUserUUID, models.UserOAuthMixin, Model):
    oauth_accounts: Mapped[list[OAuthAccount]] = relationship(lazy="joined")


class OAuthAccount(models.SQLAlchemyBaseOAuthAccount[int], Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
