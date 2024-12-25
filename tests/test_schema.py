from fastauth.schema.base import BaseSchema
from fastauth.schema import RBACMixin


def test_rbac_mixin():

    base_class = (BaseSchema, RBACMixin)

    mixin1 = type("UserRead", base_class, {})
    mixin2 = type("UserCreate", base_class, {})

    assert sorted(list(mixin1.model_fields.keys())) == sorted(
        ["role_id", "role", "permissions"]
    )

    print(mixin2.model_fields)
