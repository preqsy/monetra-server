from typing import Optional
from sqlalchemy.orm import joinedload
from core.db import get_db
from crud.base import CRUDBase
from models.category import UserCategory
from models.currency import UserCurrency
from models.user import User


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
