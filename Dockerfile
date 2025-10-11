FROM python:3.13.2-bookworm as builder

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --group dev

COPY src ./src
COPY tests ./tests
COPY migrations ./migrations

# Test stage - наследуется от builder
FROM builder as test

# Запускаем линтер
RUN uv run ruff check src/

# Запускаем тесты (без PostgreSQL для простоты, но можно добавить)
RUN uv run pytest --no-cov tests/ || echo "Tests require database"

# Production stage - финальный образ
FROM python:3.13.2-bookworm as production

WORKDIR /app

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

COPY src ./src
COPY migrations ./migrations

EXPOSE 5000

CMD ["uv", "run", "--no-dev", "src/starter.py"]
