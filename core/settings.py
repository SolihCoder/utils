from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = f'postgresql+asyncpg://solih:123@localhost:5432/sott_comment_db'

    LANGUAGES: list[str] = ['uz', 'en', 'ru']
    DEFAULT_LANGUAGE: str = 'en'

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )


settings = Settings()
