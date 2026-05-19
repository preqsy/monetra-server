from typing import Optional
from sqlalchemy.orm import joinedload
from monetra_server.core.db import get_db
from monetra_server.crud.base import CRUDBase
from monetra_server.models.category import UserCategory
from monetra_server.models.currency import UserCurrency
from monetra_server.models.user import User


class CRUDAuthUser(CRUDBase[User]):
    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_uid(self, uid: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.uid == uid)
            .options(joinedload(User.subscriptions))
            .options(joinedload(User.currencies).joinedload(UserCurrency.currency))
            .options(joinedload(User.categories).joinedload(UserCategory.category))
            .first()
        )


db_session = next(get_db())


def get_crud_auth_user() -> CRUDAuthUser:
    return CRUDAuthUser(model=User, db=db_session)
