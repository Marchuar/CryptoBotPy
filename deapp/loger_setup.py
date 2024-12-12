import logging

from constants import DEFAULT_LOGS_MODE, DEFAULT_LOG_LEVEL


def setup_logging(mode=DEFAULT_LOGS_MODE, level=DEFAULT_LOG_LEVEL):
    """
    Уровень логирования: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    # Удаляем все существующие обработчики
    logging.getLogger().handlers.clear()

    # Настраиваем формат логов
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Создаём обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Настраиваем уровень логирования
    if mode == "system":
        logging.getLogger().setLevel(level)
        logging.getLogger("apscheduler").setLevel(logging.CRITICAL)
        logging.getLogger("telegram").setLevel(logging.CRITICAL)
        logging.getLogger("httpx").setLevel(logging.CRITICAL)
    else:
        logging.getLogger().setLevel(level)

    logging.getLogger().addHandler(console_handler)
