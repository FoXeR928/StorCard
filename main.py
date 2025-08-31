import uvicorn
from loguru import logger

from instance.config_read import init_confg
from api.api_app import app

config = init_confg()

if __name__ == "__main__":
    try:
        logger.info(f"\u0421\u0435\u0440\u0432\u0435\u0440 \u0437\u0430\u043f\u0443\u0449\u0435\u043d \u043d\u0430 \u043f\u043e\u0440\u0442\u0443 {config['PORT']}")
        uvicorn.run(app=app, host="0.0.0.0", port=config["PORT"])
    except Exception as err:
        logger.error(f"\u041e\u0448\u0438\u0431\u043a\u0430 \u0438\u043d\u0438\u0446\u0438\u0430\u043b\u0438\u0437\u0430\u0446\u0438\u0438 \u0441\u0435\u0440\u0432\u0435\u0440\u0430: {err}")
    finally:
        logger.info(f"C\u0435\u0440\u0432\u0435\u0440 \u043e\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d")