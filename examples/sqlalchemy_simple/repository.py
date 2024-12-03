from fastauth.contrib.sqlalchemy.repository import SQLAlchemyUserRepository
import uuid
from .models import User


class UserRepository(SQLAlchemyUserRepository[User, uuid.UUID]):
    model = User
