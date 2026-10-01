FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --create-home appuser \
    && mkdir /app/data \
    && chown appuser:appuser /app/data

COPY --chown=appuser:appuser app ./app
USER appuser
ENV DATABASE_URL=sqlite:///app/data/db.sqlite3
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
