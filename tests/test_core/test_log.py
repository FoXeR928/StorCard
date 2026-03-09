import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, call, patch


class TestInitLog:
    @classmethod
    def setup_class(cls):
        from src.core.log import init_log

        cls.init_log = staticmethod(init_log)

    def test_init_log_success_default_params(self, tmp_path, monkeypatch):
        if "src.core.log" in sys.modules:
            del sys.modules["src.core.log"]
        monkeypatch.setattr("src.core.constants.LOGS_DIR", str(tmp_path))
        from src.core.log import init_log

        with patch("src.core.log.logger") as mock_logger:
            init_log(log_level_file="INFO", log_level_std="WARNING")
            mock_logger.remove.assert_called_once()
            assert mock_logger.add.call_count == 2
            calls = mock_logger.add.call_args_list
            file_call = calls[0]
            assert str(file_call[0][0]) == str(tmp_path / "app.log")
            assert file_call[1]["level"] == "INFO"
            assert file_call[1]["rotation"] == "256 MB"
            assert file_call[1]["retention"] == "10 days"
            assert file_call[1]["compression"] == "zip"
            assert file_call[1]["enqueue"] is True
            console_call = calls[1]
            assert console_call[0][0] == sys.stdout
            assert console_call[1]["level"] == "WARNING"
            assert console_call[1]["colorize"] is True
            assert tmp_path.exists()

    def test_init_log_with_custom_levels(self, tmp_path, monkeypatch):
        monkeypatch.setattr("src.core.constants.LOGS_DIR", str(tmp_path))
        with patch("src.core.log.logger") as mock_logger:
            self.init_log(log_level_file="DEBUG", log_level_std="ERROR")
            calls = mock_logger.add.call_args_list
            assert calls[0][1]["level"] == "DEBUG"
            assert calls[1][1]["level"] == "ERROR"

    def test_init_log_directory_creation(self, tmp_path, monkeypatch):
        log_dir = tmp_path / "logs" / "subdir"
        monkeypatch.setattr("src.core.constants.LOGS_DIR", str(log_dir))
        assert not log_dir.exists()
        with patch("src.core.log.logger"):
            with patch("pathlib.Path.mkdir") as mock_mkdir:
                self.init_log()
                mock_mkdir.assert_called_once_with(exist_ok=True)
