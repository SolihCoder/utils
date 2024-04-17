from fastapi import status
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RowAlreadyExists(HTTPException):
    def __init__(self, model: Base, field: str, value: str):
        message = {
            'uz': f"'{model.__name__}' modeli jadvalida '{field}: {value}' qiymatli qator allaqachon mavjud.",
            'en': f"Row with '{field}: {value}' in '{model.__name__}' model's table already exists."
        }
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=message['en'])


class RowDoesNotExist(HTTPException):
    def __init__(self, model: Base, values: dict):
        values = ', '.join([f"{key}: {value}" for key, value in values.items()])
        message = {
            'uz': f"'{model.__name__}' modeli jadvalida '{values}' qiymatli qator mavjud emas.",
            'en': f"Row with '{values}' in '{model.__name__}' model's table does not exist."
        }
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=message['en'])


class FieldDoesNotExist(HTTPException):
    def __init__(self, model: Base, field: str):
        message = {
            'uz': f"'{model.__name__}' modelida '{field}' nomli ustun mavjud emas.",
            'en': f"Field named '{field}' in model '{model.__name__}' does not exist."
        }
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=message['en'])


class NonNullableError(HTTPException):
    def __init__(self, model: Base, field: str):
        message = {
            'uz': f"'{model.__name__}' modelining '{field}' nomli ustuni 'None' qiymatini qabul qilmaydi.",
            'en': f"Field named '{field}' in model '{model.__name__}' does not accept 'None' value."
        }
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=message['en'])
