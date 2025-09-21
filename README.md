# RAG Server

FastAPI приложение для работы с группами, построенное на основе PostgreSQL.

## Структура проекта

```
rag-server/
├── src/                    # Исходный код приложения
│   ├── db/                 # Компоненты работы с базой данных
│   │   ├── base.py         # Базовые классы и декораторы для БД
│   │   ├── models/         # SQLAlchemy модели
│   │   │   └── group.py    # Модель группы
│   │   ├── middleware.py   # Middleware для БД
│   │   ├── session.py      # Управление сессиями БД (async)
│   │   └── transaction.py  # Управление транзакциями
│   ├── endpoints/          # REST API эндпоинты
│   │   ├── models/         # Pydantic модели для API
│   │   │   └── test_data.py
│   │   ├── routers/        # FastAPI роутеры
│   │   │   ├── groups_router.py
│   │   │   └── system_router.py
│   │   ├── groups_endpoint.py  # Логика эндпоинтов групп
│   │   └── system_endpoint.py  # Системные эндпоинты
│   ├── services/           # Бизнес-логика
│   │   └── test_service.py # Сервис для работы с группами
│   ├── utils/              # Утилиты
│   │   ├── config.py       # Конфигурация приложения
│   │   ├── logger.py       # Настройка логирования
│   │   └── shutdown.py     # Обработка завершения работы
│   ├── app_init.py         # Инициализация FastAPI приложения
│   ├── main.py             # Главный модуль с классом Main
│   └── starter.py          # Точка входа в приложение
├── tests/                  # Тесты
│   └── test_groups_endpoint.py
├── migrations/             # Миграции базы данных
│   └── 001__init.sql       # Создание таблицы groups
├── .gitignore
├── Dockerfile
├── pyproject.toml          # Конфигурация зависимостей и инструментов
└── README.md
```

## Основные папки

### `/src/db/`
Содержит все компоненты для работы с базой данных:
- **base.py** - базовые классы, декораторы (`@with_db_session`) и утилиты
- **models/** - SQLAlchemy модели данных
- **session.py** - конфигурация и управление сессиями БД

### `/src/endpoints/`
REST API слой:
- **routers/** - FastAPI роутеры с определением маршрутов
- **models/** - Pydantic модели для валидации запросов/ответов
- ***_endpoint.py** - файлы с бизнес-логикой эндпоинтов

### `/src/services/`
Бизнес-логика приложения, сервисы работают с DAO/моделями и содержат основную логику обработки данных.

### `/src/utils/`
Вспомогательные модули (конфигурация, логирование, и т.д.)

## Конфигурация

Приложение использует YAML файлы для конфигурации:

### Основная конфигурация (`src/config.yml`)
```yaml
profile: dev
server_host: 0.0.0.0
server_rest_port: 5000

db:
  host: localhost
  port: 5432
  database: rag_server
  username: # определяется в config-local.yml
  password: # определяется в config-local.yml
  migrations: ./migrations

logging:
  app_name: rag_server
  console:
    enabled: true
  graylog:
    enabled: false
    host: localhost
    port: 12201
    udp: true
  root_level: INFO
  levels:
    httpx: WARN
    openai: WARN
    uvicorn.access: WARN
```

### Локальная конфигурация (`src/config-local.yml`)
```yaml
db:
  username: postgres
  password: your_password
```

## Запуск проекта

### Требования
- Python 3.13+
- PostgreSQL
- uv (рекомендуется)

### Установка зависимостей
```bash
uv sync
uv sync --group dev  # для установки dev зависимостей
```

### Настройка базы данных
1. Создайте PostgreSQL базу данных `rag_server`
2. Обновите `src/config-local.yml` с вашими credentials
3. Миграции применяются автоматически при запуске

### Запуск приложения
```bash
uv run src/starter.py
```

Приложение будет доступно по адресу `http://localhost:5000`

### Запуск тестов
```bash
uv run pytest
uv run pytest -v  # подробный вывод
uv run pytest --cov=src  # с покрытием кода
```

### Проверка кода
```bash
uv run ruff check src/  # проверка стиля кода
uv run ruff check src/ --fix  # автоисправление
```

## API Endpoints

### Группы
- `POST /api/groups` - создание группы
- `GET /api/groups` - получение всех групп
- `GET /api/groups/{id}` - получение группы по ID
- `DELETE /api/groups/{id}` - удаление группы

### Системные
- `GET /api/goods/health` - проверка здоровья приложения
- `GET /api/goods/version` - информация о версии

## Dockerfile

Проект включает Dockerfile для контейнеризации. Для сборки и запуска:

```bash
docker build -t rag-server .
docker run -p 5000:5000 rag-server
```

## Миграции

Миграции находятся в папке `/migrations/` и используют библиотеку `yoyo-migrations`.

Пример миграции (`001__init.sql`):
```sql
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(128) NOT NULL UNIQUE
);
```

Миграции применяются автоматически при запуске приложения через `Main.run_migrations()`.

## Разработка

Проект настроен с:
- **ruff** для линтинга и форматирования
- **pytest** для тестирования
- **pre-commit** хуки для контроля качества кода
- Покрытие кода с **pytest-cov**

Для разработки рекомендуется:
1. Установить pre-commit хуки: `uv run pre-commit install`
2. Запускать тесты перед коммитом: `uv run pytest`
3. Проверять стиль кода: `uv run ruff check src/`