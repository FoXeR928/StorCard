import pytest
import json
from unittest.mock import patch
import src.core.config as config


@pytest.fixture
def mock_config_path(tmp_path):
    mock_file = tmp_path / "config.json"
    mock_dir = tmp_path / "data"
    with (
        patch("src.core.config.CONFIG_FILE", mock_file),
        patch("src.core.config.DATA_DIR", mock_dir),
    ):
        yield mock_file, mock_dir


def test_config_lifecycle(mock_config_path):
    config_file, _ = mock_config_path
    test_data = {"db_url": "sqlite:///test.db", "debug": True}
    assert config.check_config() is False
    config.config_create(test_data)
    assert config.check_config() is True
    loaded_data = config.get_db_config()
    assert loaded_data == test_data
    assert loaded_data["debug"] is True


def test_get_db_config_json_error(mock_config_path):
    config_file, _ = mock_config_path
    config_file.write_text("invalid json {", encoding="utf-8")
    with patch("src.core.system.stop_server") as mock_stop:
        config.get_db_config()
        mock_stop.assert_called_once_with(1)


def test_config_create_permission_error(mock_config_path):
    _, data_dir = mock_config_path
    data_dir.mkdir(parents=True, exist_ok=True)
    try:
        data_dir.chmod(0o444)
        assert config.config_create({"test": 1})
    finally:
        data_dir.chmod(0o755)


def test_get_db_config_not_found(mock_config_path):
    config_file, _ = mock_config_path
    if config_file.exists():
        config_file.unlink()
    with patch("src.core.system.stop_server") as mock_stop:
        config.get_db_config()
        mock_stop.assert_called_once_with(1)
