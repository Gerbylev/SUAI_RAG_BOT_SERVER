# Правила разработки проекта

## Архитектура проекта
- **Приложение полностью асинхронное** с использованием FastAPI
- Все функции должны быть `async`
- Использовать `await` для всех асинхронных операций
- Стек: FastAPI + SQLAlchemy + AsyncPG + Uvicorn

## Импорты
- **Только глобальные импорты в начале файла**
- Запрещены локальные импорты внутри функций
- Все зависимости импортируются в верхней части файла

```python
# ✅ Правильно
import asyncio
from typing import Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_current_session

async def my_function():
    session = get_current_session()
    pass

# ❌ Неправильно
async def my_function():
    from db.session import get_current_session  # локальный импорт запрещен
```

## Работа с базой данных
- **Использовать SQLAlchemy с AsyncPG драйвером**
- Использовать декоратор `@transactional` для операций изменения данных
- Сессии управляются через scoped session с ContextVar
- Доступ к текущей сессии через `get_current_session()`

```python
# ✅ Правильно
from db.transaction import transactional
from db.session import get_current_session

@transactional
async def update_group(group_id: int, name: str):
    session = get_current_session()
    # операции с БД автоматически в транзакции

# ❌ Неправильно
async def update_group(group_id: int, name: str):
    session = get_current_session()
    # нет декоратора @transactional для изменения данных
```

## Работа с конфигурацией
- Конфигурация загружается из YAML файлов через `ConfigLoader`
- Приоритет конфигураций: переменные окружения → config-local.yml → config-{profile}.yml → config.yml
- Доступ к конфигу через глобальную переменную `CONFIG`
- Конфигурация типизирована через dataclasses

```python
# ✅ Правильно
from utils.config import CONFIG

async def connect_to_db():
    host = CONFIG.db.host
    port = CONFIG.db.port

# ❌ Неправильно
import os
async def connect_to_db():
    host = os.getenv("DB_HOST")  # использование переменных окружения напрямую
```

## Структура проекта
```
src/
├── main.py              # Точка входа приложения
├── app_init.py          # Инициализация FastAPI приложения
├── starter.py           # Стартер приложения
├── db/
│   ├── session.py       # Управление сессиями БД
│   ├── transaction.py   # Декоратор @transactional
│   └── middleware.py    # Middleware для БД
├── dao/                 # Data Access Objects
├── endpoints/           # REST API endpoints
├── services/            # Бизнес-логика
└── utils/
    ├── config.py        # Конфигурация
    ├── logger.py        # Логирование
    └── shutdown.py      # Graceful shutdown
```

## Тестирование и проверка работоспособности
- Запуск тестов: `uv run pytest`
- Проверка типов: `uv run pyright`
- Линтер: `uv run ruff check`
- Форматирование: `uv run ruff format`
- Установка зависимостей: `uv sync`

## Логирование
- Использовать `get_logger("ModuleName")` для получения логгера
- Логи настраиваются через конфигурацию (console + graylog)
- Логирование ошибок в транзакциях происходит автоматически

## Управление зависимостями
- Используется `uv` для управления зависимостями
- Зависимости описаны в `pyproject.toml`
- Разделение на основные зависимости и dev-зависимости

## Other recommendations

- Do not generate .MD files when not asked to do that.
