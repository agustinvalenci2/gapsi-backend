from app.core.config import get_settings
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise


def register_database(app: FastAPI) -> RegisterTortoise:
    settings = get_settings()
    return RegisterTortoise(
        app,
        db_url=settings.database_url,
        modules={"models": ["app.models.user", "app.models.incident"]},
        generate_schemas=settings.generate_schemas,
        use_tz=True,
        timezone="UTC",
    )
