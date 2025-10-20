from typing import List, Optional, TypeVar, Generic, Type
from sqlalchemy.orm import Session
from storage.database import Base, db_manager

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.session: Optional[Session] = None

    def __enter__(self):
        self.session = db_manager.get_session()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            db_manager.close_session(self.session)
            self.session = None

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получение записи по ID"""
        return self.session.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получение всех записей с пагинацией"""
        return self.session.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj: ModelType) -> ModelType:
        """Создание новой записи"""
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, id: int, update_data: dict) -> Optional[ModelType]:
        """Обновление записи"""
        obj = self.get_by_id(id)
        if obj:
            for field, value in update_data.items():
                setattr(obj, field, value)
            self.session.commit()
            self.session.refresh(obj)
        return obj

    def delete(self, id: int) -> bool:
        """Удаление записи"""
        obj = self.get_by_id(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False

    def get_or_create(self, defaults: dict = None, **kwargs) -> tuple[ModelType, bool]:
        """Получить или создать запись"""
        obj = self.session.query(self.model).filter_by(**kwargs).first()
        if obj:
            return obj, False
        
        if defaults:
            kwargs.update(defaults)
        
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj, True

    def bulk_create(self, objects: List[ModelType]) -> List[ModelType]:
        """Массовое создание записей"""
        self.session.bulk_save_objects(objects)
        self.session.commit()
        return objects