from loguru import logger
import os
import sys


def reboot_server(delay: int = 1):
    try:
        if delay:
            time.sleep(delay)
        logger.warning("Выполнение перезагрузки сервера...")
        logger.remove() 
        executable = sys.executable
        args = [executable] + sys.argv
        os.execv(executable, args)
    except Exception as err:
        logger.critical(f"Не удалось выполнить автоматический перезапуск: {err}")
        sys.exit(1)