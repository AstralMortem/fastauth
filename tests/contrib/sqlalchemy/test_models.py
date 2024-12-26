from fastauth.contrib.sqlalchemy.models import *


# To get 100% coverage
def test_models():
    assert SQLAlchemyBaseUserUUID.__name__ == "SQLAlchemyBaseUserUUID"
    assert SQLAlchemyBaseRole.__name__ == "SQLAlchemyBaseRole"
    assert SQLAlchemyBaseUser.__name__ == "SQLAlchemyBaseUser"
    assert SQLAlchemyBasePermission.__name__ == "SQLAlchemyBasePermission"
    assert SQLAlchemyBaseRolePermissionRel.__name__ == "SQLAlchemyBaseRolePermissionRel"
    assert SQLAlchemyBaseOAuthAccount.__name__ == "SQLAlchemyBaseOAuthAccount"
    assert SQLAlchemyBaseUserPermissionRel.__name__ == "SQLAlchemyBaseUserPermissionRel"
    assert SQLAlchemyBaseOAuthAccountUUID.__name__ == "SQLAlchemyBaseOAuthAccountUUID"
