from loguru import logger
import os
import sys


def reboot_server():
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
        logger.info("Server restart")
    except Exception as err:
        logger.error(f"Server not restart. Please, restart it. Error: {err}")
