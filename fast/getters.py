from typing import Any

from fastapi import Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, joinedload

from core.settings import settings
from .exceptions import RowDoesNotExist
from .creators import create

Base = declarative_base()


async def get_language(request: Request) -> str:
    content_language = request.headers.get('content-language')

    if content_language in settings.LANGUAGES:
        return content_language
    else:
        return settings.DEFAULT_LANGUAGE


async def extract_user_id(request: Request, header_name='user-id'):
    user_id = request.headers.get(header_name, None)
    user_id = int(user_id) if user_id else None
    return user_id


### QUERIES ###

#DONE
async def get(model: Base, db: AsyncSession, order_by: str | tuple[str] | list[str] = 'id', filters: dict[str, Any] = None, limit: int = None, offset: int = None):
    stmt = select(model).order_by(*tuple(order_by)) if not filters else select(model).order_by(*tuple(order_by)).where(*(getattr(model, key) == value for key, value in filters.items()))

    if all(arg is not None for arg in [limit, offset]):
        stmt = stmt.limit(limit).offset(offset)

    instances = (await db.execute(stmt)).scalars().all()
    return instances

#DONE
async def get_one(model: Base, db: AsyncSession, order_by: str | tuple[str] | list[str] = 'id', filters: dict[str, Any] = None, strict: bool = True) -> Base | None:
    stmt = select(model).order_by(*tuple(order_by)) if not filters else select(model).order_by(*order_by).where(*(getattr(model, key) == value for key, value in filters.items()))

    return (await db.execute(stmt)).scalar_one_or_none() if strict else (await db.execute(stmt)).scalars().first()


async def get_all_by_field(model: Base, field: str, value: Any, db: AsyncSession, limit: int | None = None, offset: int | None = None, join: str | None = None) -> Base:
    stmt = select(model).where(getattr(model, field) == value).order_by(model.id.asc())
    if join:
        stmt = stmt.options(joinedload(getattr(model, join, None)))
    if limit:
        stmt = stmt.limit(limit).offset(offset)

    instances = (await db.execute(stmt)).unique().scalars().all()
    return instances


async def get_one_by_id(model: Base, model_id: int, db: AsyncSession) -> Base:
    instance = (await db.execute(select(model).where(model.id == model_id))).scalar_one_or_none()
    if instance:
        return instance
    else:
        raise RowDoesNotExist(model, 'id', model_id)
