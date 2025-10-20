from typing import List, Optional, TypeVar, Generic, Type, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from storage.database import Base, db_manager

ModelType = TypeVar("ModelType", bound=Base)

class AsyncBaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Получение записи по ID"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(select(self.model).filter(self.model.id == id))
            return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Получение всех записей с пагинацией"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(
                select(self.model).offset(skip).limit(limit)
            )
            return result.scalars().all()

    async def create(self, **kwargs) -> ModelType:
        """Создание новой записи из ключевых слов"""
        async with db_manager.get_async_session() as session:
            obj = self.model(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def create_from_obj(self, obj: ModelType) -> ModelType:
        """Создание новой записи из объекта модели"""
        async with db_manager.get_async_session() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def update(self, id: int, update_data: dict) -> Optional[ModelType]:
        """Обновление записи"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(select(self.model).filter(self.model.id == id))
            obj = result.scalar_one_or_none()
            
            if obj:
                for field, value in update_data.items():
                    setattr(obj, field, value)
                await session.commit()
                await session.refresh(obj)
            return obj

    async def delete(self, id: int) -> bool:
        """Удаление записи"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(select(self.model).filter(self.model.id == id))
            obj = result.scalar_one_or_none()
            
            if obj:
                await session.delete(obj)
                await session.commit()
                return True
            return False

    async def get_or_create(self, defaults: dict = None, **kwargs) -> tuple[ModelType, bool]:
        """Получить или создать запись"""
        async with db_manager.get_async_session() as session:
            result = await session.execute(select(self.model).filter_by(**kwargs))
            obj = result.scalar_one_or_none()
            
            if obj:
                return obj, False
            
            if defaults:
                kwargs.update(defaults)
            
            obj = self.model(**kwargs)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj, True