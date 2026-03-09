import pytest
import sys
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_all(monkeypatch):
    mock_logger = MagicMock()
    mock_sleep = MagicMock()
    mock_execv = MagicMock()
    mock_exit = MagicMock()
    monkeypatch.setattr("src.core.system.logger", mock_logger)
    monkeypatch.setattr("src.core.system.time.sleep", mock_sleep)
    monkeypatch.setattr("src.core.system.os.execv", mock_execv)
    monkeypatch.setattr("src.core.system.sys.exit", mock_exit)
    return {
        "logger": mock_logger,
        "sleep": mock_sleep,
        "execv": mock_execv,
        "exit": mock_exit,
    }


@pytest.fixture
def mock_logger(mock_all):
    return mock_all["logger"]


@pytest.fixture
def mock_sleep(mock_all):
    return mock_all["sleep"]


@pytest.fixture
def mock_execv(mock_all):
    return mock_all["execv"]


@pytest.fixture
def mock_exit(mock_all):
    return mock_all["exit"]


@pytest.fixture
def mock_remove(mock_logger):
    return mock_logger.remove


@pytest.fixture
def mock_sys_argv():
    original_argv = sys.argv.copy()
    yield
    sys.argv = original_argv


@pytest.fixture
def mock_sys_executable(monkeypatch):
    monkeypatch.setattr("sys.executable", "/test/bin/python")
    yield


@pytest.fixture
def capture_logs():
    logs = []

    def sink(message):
        logs.append(str(message))

    from loguru import logger

    logger_id = logger.add(sink, format="{message}")
    yield logs
    logger.remove(logger_id)
