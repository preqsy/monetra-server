from typing import Type, TypeVar, Generic

from pydantic import BaseModel

from core.db import get_db, Base
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session = next(get_db())):
        self.db = db
        self.model = model

    def create(self, data_obj: dict) -> ModelType:
        if isinstance(data_obj, BaseModel):
            data_obj = data_obj.model_dump()

        data_obj = self.model(**data_obj)
        try:
            self.db.add(data_obj)
            self.db.commit()
            self.db.refresh(data_obj)
        except Exception:
            self.db.rollback()
            raise
        return data_obj

    def get(self, id: int) -> ModelType | None:
        return self._get_query_by_id(id).first()

    def bulk_insert(self, data_obj: list[dict]) -> list[ModelType]:
        data_list = [self.model(**data) for data in data_obj]
        try:
            self.db.bulk_save_objects(objects=data_list, return_defaults=True)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        return data_list

    def _get_query_by_id(self, id: int):
        return self.db.query(self.model).filter(self.model.id == id)

    def update(self, id: int, data_obj: dict) -> ModelType | None:
        if isinstance(data_obj, BaseModel):
            data_obj = data_obj.model_dump(exclude_unset=True)

        existing_obj = self._get_query_by_id(id)
        if not existing_obj.first():
            return None

        existing_obj.update(data_obj)
        self.db.commit()
        return existing_obj.first()

    def delete(self, id):
        existing_obj = self._get_query_by_id(id)
        if not existing_obj.first():
            return None

        existing_obj.delete(synchronize_session=False)
        self.db.commit()
        return None
