import uvicorn
from sys import stdout
import os
from loguru import logger

from api.api_app import app


def init_log(log_level_file="INFO", log_level_std="WARNING"):
    try:
        logger.remove()
        logger.add(
            "logs/app.log",
            format="{time} | {level} | {message} | {name}",
            rotation="256 MB",
            retention=f"10 days",
            level=log_level_file,
        )
        if bool(int(get_config(name='debug'))) == True:
            log_level_std = "TRACE"
        logger.add(stdout, level=log_level_std)
        logger.info("\u0418\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0438\u0440\u043e\u0432\u0430\u043d \u0444\u0430\u0439\u043b \u043b\u043e\u0433\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f")
    except Exception as err:
        logger.error(f"\u041e\u0448\u0438\u0431\u043a\u0430 \u0438\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u0438 \u043a\u043e\u043d\u0444\u0438\u0433\u043e\u0432 \u0431\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445: {err}")
        exit()

if os.path.exists("./instance/config.json")==True:
    from db_modules.db_query_config import get_config
    port=int(get_config(name="app_port"))
    init_log()
else:
    port=7000

if __name__ == "__main__":
    try:
        logger.info(f"\u0421\u0435\u0440\u0432\u0435\u0440 \u0437\u0430\u043f\u0443\u0449\u0435\u043d \u043d\u0430 \u043f\u043e\u0440\u0442\u0443 {port}")
        uvicorn.run(app=app, host="0.0.0.0", port=port)
    except Exception as err:
        logger.error(f"\u041e\u0448\u0438\u0431\u043a\u0430 \u0438\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u0438 \u0441\u0435\u0440\u0432\u0435\u0440\u0430: {err}")
    finally:
        logger.info(f"C\u0435\u0440\u0432\u0435\u0440 \u043e\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d")