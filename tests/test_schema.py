from fastauth.schema.base import BaseSchema


class UserRead(BaseSchema):
    id: int


def test_user():
    print(UserRead.model_fields)
