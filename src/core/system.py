from loguru import logger
import time
import os
import sys


def reboot_server(delay: int = 1):
    try:
        if delay > 0:
            logger.info(f"Перезагрузка через {delay} сек...")
            time.sleep(delay)
        logger.warning("Выполнение перезагрузки сервера...")
        logger.remove()
        executable = sys.executable
        os.execv(executable, [executable] + sys.argv)
    except Exception as err:
        logger.add(sys.stderr)
        logger.critical(f"Не удалось выполнить автоматический перезапуск: {err}")
        sys.exit(1)


def stop_server(status: int = 0):
    try:
        logger.info(f"Завершение работы сервера (код: {status})")
        logger.remove()
    finally:
        sys.exit(status)
