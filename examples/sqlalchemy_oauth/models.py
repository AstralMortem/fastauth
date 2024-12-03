from typing import List
from sqlalchemy.orm import relationship, Mapped
from fastauth.contrib.sqlalchemy import models
from examples.db import Model


class User(models.SQLAlchemyUserUUID, Model):
    oauth_accounts: Mapped[List["OAuthAccount"]] = relationship(lazy="joined")


class OAuthAccount(models.SQLAlchemyOAuthAccountUUID, Model):
    pass
