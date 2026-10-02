from app.core.database import database_config


def test_cloud_sql_socket_is_preserved():
    connection = database_config(
        "postgres://demo:example%3Apassword@/postgres"
        "?host=%2Fcloudsql%2Fexample%3Aus-east4%3Ademo&max_size=5"
    )["connections"]["default"]
    assert connection["engine"] == "tortoise.backends.asyncpg"
    assert connection["credentials"]["host"] == "/cloudsql/example:us-east4:demo"
    assert connection["credentials"]["database"] == "postgres"
    assert connection["credentials"]["password"] == "example:password"
    assert connection["credentials"]["max_size"] == 5


def test_postgres_tcp_connection():
    credentials = database_config(
        "postgres://demo:example@db:5433/demo"
    )["connections"]["default"]["credentials"]
    assert credentials["host"] == "db"
    assert credentials["port"] == 5433


def test_sqlite_demo_connection():
    connection = database_config("sqlite:///app/data/db.sqlite3")["connections"]["default"]
    assert connection["engine"] == "tortoise.backends.sqlite"
    assert connection["credentials"]["file_path"] == "/app/data/db.sqlite3"
