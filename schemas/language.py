from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LanguageInSchema(BaseModel):
    title: str

    model_config = ConfigDict(
        from_attributes=True
    )


class LanguageOutSchema(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
