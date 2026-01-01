FROM python:3.11-slim

WORKDIR /app

COPY apps/api/pyproject.toml /app/pyproject.toml
COPY packages/waterpolo /app/packages/waterpolo

RUN pip install --no-cache-dir -U pip \
    && pip install --no-cache-dir -e /app/packages/waterpolo \
    && pip install --no-cache-dir .

COPY apps/api/app /app/app
COPY apps/api/alembic.ini /app/alembic.ini
COPY apps/api/alembic /app/alembic

ENV PYTHONPATH=/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
