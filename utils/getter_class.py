from typing import Any

from pydantic import BaseModel
from sqlalchemy import select, exists, inspect, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from .exceptions import RowDoesNotExist, NonNullableError, FieldDoesNotExist

Base = declarative_base()


class Repository:
    def __init__(self, model: Base, db: AsyncSession):
        self.model = model
        self.db = db

    async def create(self, payload: BaseModel, extra: dict[str, Any] = None, exclude: list[str] | set[str] | str = None) -> Base:
        payload = {**payload.model_dump(), **set(extra)} if extra else payload.model_dump()
        exclude = set(exclude) if exclude else set()
        payload = {key: value for key, value in payload.items() if key not in exclude}
        for key, value in payload.items():
            if value is None:
                if not await self.is_none_allowed(key):
                    raise NonNullableError(self.model, key)

        instance = self.model(**payload)
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)

        return instance

    async def all(self, order_by: str | tuple[str] | list[str] = 'id', limit: int = None, offset: int = None):
        stmt = select(self.model).order_by(*tuple(order_by))

        if all(arg is not None for arg in [limit, offset]):
            stmt = stmt.limit(limit).offset(offset)

        return (await self.db.execute(stmt)).scalars().all()

    async def filter(self, filters: dict[str, Any], join_condition: str, order_by: str | tuple[str] | list[str] = 'id', limit: int = None, offset: int = None):
        condition = await self.get_condition(filters=filters, join_condition=join_condition)
        stmt = select(self.model).order_by(*tuple(order_by)).where(condition)

        if all(arg is not None for arg in [limit, offset]):
            stmt = stmt.limit(limit).offset(offset)

        return (await self.db.execute(stmt)).scalars().all()

    async def get_one(self, filters: dict[str, Any], join_condition: str):
        condition = await self.get_condition(filters=filters, join_condition=join_condition)
        stmt = select(self.model).where(condition)

        result = (await self.db.execute(stmt)).scalar_one_or_none()

        if not result:
            raise RowDoesNotExist(model=self.model, values=filters)

        return result

    async def get_or_create_one(self, payload: dict | BaseModel, ignore_non_unique: bool):
        if issubclass(payload.__class__, BaseModel):
            payload = payload.model_dump()

        if ignore_non_unique:
            unique_fields = await self.get_unique_fields()
            payload = {key: value for key, value in payload.items() if key in unique_fields}

        if await self.exists(filters=payload, join_condition='or' if ignore_non_unique else 'and'):
            result = await self.get_one(filters=payload, )

    async def exists(self, filters: dict[str, Any] = None, join_condition: str | None = None) -> bool:
        condition = await self.get_condition(filters=filters if filters else {'id': None}, join_condition=join_condition)
        stmt = select(exists().where(condition))

        return (await self.db.execute(stmt)).scalar()

    async def ensure_exists(self, filters: dict[str, Any] = None) -> bool:
        if not self.exists(filters):
            raise RowDoesNotExist(model=self.model, values=filters)
        else:
            return True

    async def get_unique_fields(self) -> set:
        return {column.key for column in inspect(self.model).columns if column.unique}

    async def get_condition(self, filters: dict[str, Any], join_condition: str = 'and'):
        if join_condition == 'and':
            condition = and_(*(getattr(self.model, key) == value for key, value in filters.items()))
        elif join_condition == 'or':
            condition = or_(*(getattr(self.model, key) == value for key, value in filters.items()))
        else:
            raise ValueError('join_condition must be either "and" or "or"')

        return condition

    async def is_none_allowed(self, field_name: str) -> bool:
        field = getattr(self.model, field_name, None)

        if not field:
            raise FieldDoesNotExist(model=self.model, field=field_name)

        return field.nullable

    async def ensure_payload_valid(self, payload: dict) -> None:
        for key, value in payload.items():
            field = getattr(self.model, key, None)
            if not field:
                raise FieldDoesNotExist(model=self.model, field=key)


            if value is None:
                if not await self.is_none_allowed(key):
                    raise NonNullableError(self.model, key)
