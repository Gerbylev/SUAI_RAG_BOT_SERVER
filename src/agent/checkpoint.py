
from utils.config import CONFIG


def get_checkpoint_connection_string() -> str:
    """Возвращает строку подключения для PostgresSaver"""
    db_config = CONFIG.db
    return (
        f"postgresql://{db_config.username}:{db_config.password}"
        f"@{db_config.host}:{db_config.port}/{db_config.database}"
    )