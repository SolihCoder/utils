import os
from typing import Iterable, Sequence

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

from .validators import make_sure_exists_by_ids

Base = declarative_base()


async def delete_by_ids(model: Base, model_ids: set[int] | list[int] | tuple[int] | int | str, db: AsyncSession) -> None:
    if not isinstance(model_ids, Iterable) and not isinstance(model_ids, Sequence):
        model_ids = {model_ids}

    await make_sure_exists_by_ids(model, model_ids, db)
    await db.execute(delete(model).where(model.id.in_(model_ids)))
    await db.commit()


async def delete_project_file(file: str) -> bool:
    project_dir = os.getcwd()
    file_path = os.path.join(project_dir, file)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f'Successfully Deleted: {file} ({file_path})')
        return True
    else:
        print(f'Does Not Exist: {file} ({file_path})')
        return False
