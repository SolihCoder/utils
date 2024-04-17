from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from .exceptions import NonNullableError
from .getters import get_all
from .validators import verify_none_allowed

Base = declarative_base()


async def deactivate_all_if_is_active(model: Base, payload: BaseModel, db: AsyncSession) -> None:
    if payload.is_active:
        all_instances = await get_all(model=model, db=db)
        for instance in all_instances:
            instance.is_active = False
    await db.commit()


async def update_model_with_payload(instance: Base, payload: BaseModel | dict, db: AsyncSession, exclude: list | set | str = None) -> Base:
    if exclude:
        exclude = set(exclude)
    else:
        exclude = set()

    if isinstance(payload, dict):
        payload = payload.items()

    for key, value in payload:
        if key not in exclude:
            if value == '':
                if await verify_none_allowed(instance.__class__, key):
                    setattr(instance, key, None)
                else:
                    raise NonNullableError(instance.__class__, key)
            if value is not None:
                setattr(instance, key, value)
    await db.commit()
    await db.refresh(instance)
    return instance
