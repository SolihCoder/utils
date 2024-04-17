from typing import Sequence, Iterable

from pydantic import BaseModel
from sqlalchemy import exists
from sqlalchemy import func, not_, and_
from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base

from .exceptions import RowAlreadyExists, RowDoesNotExist, FieldDoesNotExist
from .getters import get

Base = declarative_base()

async def unique_validator(model: Base, schema: BaseModel, db_session: AsyncSession, case_strict: bool | None = False, exclude_id: str | int | None = None) -> bool:
    model_unique_fields = {column.key for column in inspect(model).columns if column.unique}
    corresponding_schema_fields = {field for field in schema.model_fields.keys() if field in model_unique_fields}

    for field in corresponding_schema_fields:
        model_part = func.lower(getattr(model, field)) if case_strict else getattr(model, field)
        schema_part = func.lower(getattr(schema, field)) if case_strict else getattr(schema, field)

        if exclude_id:
            query = select(exists().where(and_(model_part == schema_part, not_(model.id == exclude_id))))
        else:
            query = select(exists().where(model_part == schema_part))

        result = (await db_session.execute(query)).scalar()

        if result is True:
            raise RowAlreadyExists(model, field, getattr(schema, field))

    return True


async def verify_exists_by_ids(model: Base, model_ids: list[int] | set[int] | int, db: AsyncSession) -> tuple:
    if not isinstance(model_ids, Iterable) and not isinstance(model_ids, Sequence):
        model_ids = {model_ids}

    for model_id in model_ids:
        result = (await db.execute(select(exists().where(model.id == model_id)))).scalar()
        if result:
            return True, model_id

    return False, None


async def make_sure_exists_by_ids(model: Base, model_ids: list[int] | set[int] | int, db: AsyncSession):
    result, non_existent_id = await verify_exists_by_ids(model, model_ids, db)
    if not result:
        raise RowDoesNotExist(model, 'id', non_existent_id)


async def verify_none_allowed(model: Base, field: str) -> bool:
    field = getattr(model, field, None)
    if not field:
        raise FieldDoesNotExist(model, field)
    if not field.nullable:
        return False
    elif field.nullable:
        return True
    else:
        return False
