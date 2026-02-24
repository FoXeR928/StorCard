from loguru import logger


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
        logger.add(stdout, level=log_level_std)
        logger.success("Log init")
    except Exception as err:
        logger.error(f"Log not init. Error: {err}")
        exit()
