"""Container startup with self-contained SQLite defaults for demos."""

import os
import secrets
import sys


def main() -> None:
    if os.environ.get("DATABASE_URL", "").startswith("sqlite://"):
        os.environ.setdefault("GENERATE_SCHEMAS", "true")
        if "JWT_SECRET_KEY" not in os.environ:
            os.environ["JWT_SECRET_KEY"] = secrets.token_urlsafe(48)
            print(
                "SQLite demo: generated a temporary JWT key; "
                "tokens expire when the container restarts.",
                flush=True,
            )

    os.execv(
        sys.executable,
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            os.environ.get("PORT") or "8000",
        ],
    )


if __name__ == "__main__":
    main()
