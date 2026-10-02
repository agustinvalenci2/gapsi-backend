from urllib.parse import parse_qs, urlsplit

from app.core.config import get_settings
from fastapi import FastAPI
from tortoise.backends.base.config_generator import generate_config
from tortoise.contrib.fastapi import RegisterTortoise


def database_config(database_url: str) -> dict:
    config = generate_config(
        database_url,
        app_modules={"models": ["app.models.user", "app.models.incident"]},
    )
    url = urlsplit(database_url)
    if url.scheme in {"postgres", "postgresql", "asyncpg", "psycopg"}:
        hosts = parse_qs(url.query).get("host")
        if hosts:
            # Tortoise replaces the query host with the authority hostname,
            # losing Cloud SQL Unix sockets when the authority host is empty.
            config["connections"]["default"]["credentials"]["host"] = hosts[-1]
    return config


def register_database(app: FastAPI) -> RegisterTortoise:
    settings = get_settings()
    return RegisterTortoise(
        app,
        config=database_config(settings.database_url),
        generate_schemas=settings.generate_schemas,
        use_tz=True,
        timezone="UTC",
    )
