import pytest
from pathlib import Path
from loguru import logger
from unittest.mock import patch
import src.core.log as log


@pytest.fixture(autouse=True)
def clean_loguru():
    logger.remove()
    yield
    logger.remove()


def test_init_log_success(test_dirs):
    temp_logs = test_dirs["logs"]
    with patch("src.core.log.LOGS_DIR", temp_logs):
        log.init_log(log_level_file="DEBUG", log_level_std="DEBUG")
        logger.info("Test message")
        logger.remove()
        log_file = temp_logs / "app.log"
        assert (
            log_file.exists()
        ), f"Лог не создался в {temp_logs}. Содержимое: {list(temp_logs.iterdir())}"
        assert "Test message" in log_file.read_text()


def test_init_log_permission_error(test_dirs):
    with patch("src.core.log.LOGS_DIR") as mock_path:
        mock_path.mkdir.side_effect = PermissionError("Access denied")
        mock_path.exists.return_value = False
        with pytest.raises(SystemExit) as exc:
            log.init_log()
        assert exc.value.code == 1
