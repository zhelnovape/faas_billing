FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Зависимости берём из pyproject.toml (единый источник правды).
# Слой кэшируется, пока pyproject.toml не изменился.
COPY pyproject.toml ./
RUN python -c "import tomllib; print('\n'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))" > /tmp/requirements.txt \
    && pip install -r /tmp/requirements.txt

COPY alembic.ini ./
COPY app ./app
COPY migrations ./migrations

RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# 1) применяем миграции, 2) запускаем API
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
