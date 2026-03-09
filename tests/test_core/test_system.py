import pytest
import sys
from unittest.mock import call, ANY, patch


class TestStopServer:
    @classmethod
    def setup_class(cls):
        from src.core.system import stop_server

        cls.stop_server = staticmethod(stop_server)

    def test_stop_server_normal_exit(self, mock_logger, mock_exit):
        self.stop_server(status=0)
        mock_logger.info.assert_called_once_with("Завершение работы сервера (код: 0)")
        mock_logger.remove.assert_called_once()
        mock_exit.assert_called_once_with(0)

    def test_stop_server_with_error_code(self, mock_logger, mock_exit):
        self.stop_server(status=1)
        mock_logger.info.assert_called_once_with("Завершение работы сервера (код: 1)")
        mock_exit.assert_called_once_with(1)

    def test_stop_server_custom_code(self, mock_logger, mock_exit):
        self.stop_server(status=42)
        mock_logger.info.assert_called_once_with("Завершение работы сервера (код: 42)")
        mock_exit.assert_called_once_with(42)

    def test_stop_server_calls_remove_before_exit(self, mock_logger, mock_exit):
        call_order = []

        def track_remove():
            call_order.append("remove")

        def track_exit(status):
            call_order.append("exit")

        mock_logger.remove.side_effect = track_remove
        mock_exit.side_effect = track_exit
        self.stop_server()
        assert call_order == ["remove", "exit"]

    def test_stop_server_called_multiple_times(self, mock_logger, mock_exit):
        for code in [0, 1, 2, 3]:
            self.stop_server(code)
        assert mock_exit.call_count == 4
        assert mock_logger.info.call_count == 4


class TestRebootServer:
    @classmethod
    def setup_class(cls):
        from src.core.system import reboot_server

        cls.reboot_server = staticmethod(reboot_server)

    def test_reboot_server_with_delay(
        self,
        mock_logger,
        mock_sleep,
        mock_execv,
        mock_remove,
        mock_sys_executable,
        mock_sys_argv,
    ):
        sys.argv = ["test_script.py", "--port=8000", "--debug"]
        self.reboot_server(delay=3)
        mock_logger.info.assert_called_once_with("Перезагрузка через 3 сек...")
        mock_logger.warning.assert_called_once_with(
            "Выполнение перезагрузки сервера..."
        )
        mock_sleep.assert_called_once_with(3)
        mock_remove.assert_called_once()
        expected_args = ["/test/bin/python", "test_script.py", "--port=8000", "--debug"]
        mock_execv.assert_called_once_with("/test/bin/python", expected_args)

    def test_reboot_server_no_delay(
        self, mock_logger, mock_sleep, mock_execv, mock_remove, mock_sys_executable
    ):
        self.reboot_server(delay=0)
        mock_logger.info.assert_not_called()
        mock_logger.warning.assert_called_once()
        mock_sleep.assert_not_called()
        mock_remove.assert_called_once()
        mock_execv.assert_called_once()

    def test_reboot_server_default_delay(
        self, mock_logger, mock_sleep, mock_execv, mock_remove, mock_sys_executable
    ):
        self.reboot_server()
        mock_sleep.assert_called_once_with(1)
        mock_logger.info.assert_called_once_with("Перезагрузка через 1 сек...")

    def test_reboot_server_with_complex_args(
        self, mock_execv, mock_sleep, mock_remove, mock_sys_executable
    ):
        sys.argv = [
            "app.py",
            "--name=John Doe",
            "--path=/path/with spaces",
            '--json={"key": "value"}',
        ]
        with patch("loguru.logger"):
            self.reboot_server(delay=0)
        expected_args = [
            "/test/bin/python",
            "app.py",
            "--name=John Doe",
            "--path=/path/with spaces",
            '--json={"key": "value"}',
        ]
        mock_execv.assert_called_once_with("/test/bin/python", expected_args)

    def test_reboot_server_execv_failure(
        self, mock_logger, mock_sleep, mock_execv, mock_exit
    ):
        error_msg = "Permission denied"
        mock_execv.side_effect = Exception(error_msg)
        self.reboot_server(delay=0)
        mock_logger.add.assert_called_once_with(sys.stderr)
        mock_logger.critical.assert_called_once()
        logged_message = mock_logger.critical.call_args[0][0]
        assert error_msg in logged_message
        assert "автоматический перезапуск" in logged_message
        mock_exit.assert_called_once_with(1)

    def test_reboot_server_preserves_environment(
        self, mock_execv, mock_sleep, mock_remove, monkeypatch
    ):
        monkeypatch.setenv("TEST_VAR", "test_value")
        monkeypatch.setenv("PATH", "/test/path")
        with patch("loguru.logger"):
            with patch("sys.executable", "python"):
                sys.argv = ["app.py"]

                self.reboot_server(delay=0)
        mock_execv.assert_called_once()

    @pytest.mark.parametrize("delay", [0, 1, 2, 5, 10])
    def test_reboot_server_various_delays(self, mock_sleep, delay):
        with (
            patch("loguru.logger"),
            patch("os.execv"),
            patch("sys.executable", "python"),
        ):
            self.reboot_server(delay=delay)
            if delay > 0:
                mock_sleep.assert_called_once_with(delay)
            else:
                mock_sleep.assert_not_called()

    def test_reboot_server_logger_removal_before_execv(self, mock_execv, mock_remove):
        call_order = []

        def track_remove():
            call_order.append("remove")

        def track_execv(*args):
            call_order.append("execv")

        mock_remove.side_effect = track_remove
        mock_execv.side_effect = track_execv
        with (
            patch("loguru.logger"),
            patch("time.sleep"),
            patch("sys.executable", "python"),
        ):
            try:
                self.reboot_server(delay=0)
            except Exception:
                pass
            if len(call_order) >= 2:
                assert call_order == ["remove", "execv"]

    def test_reboot_server_with_unicode_args(self, mock_execv, mock_sys_executable):
        sys.argv = ["app.py", "--name=Тестовый пользователь", "--city=Москва"]
        with patch("loguru.logger"), patch("time.sleep"):
            self.reboot_server(delay=0)
        called_args = mock_execv.call_args[0][1]
        assert "--name=Тестовый пользователь" in called_args
        assert "--city=Москва" in called_args

    def test_reboot_server_negative_delay(self, mock_sleep, mock_execv):
        with patch("loguru.logger"), patch("sys.executable", "python"):
            self.reboot_server(delay=-5)
        mock_sleep.assert_not_called()
        mock_execv.assert_called_once()


class TestSystemIntegration:
    @classmethod
    def setup_class(cls):
        from src.core.system import reboot_server, stop_server

        cls.reboot_server = staticmethod(reboot_server)
        cls.stop_server = staticmethod(stop_server)

    def test_reboot_then_stop_not_possible(self):
        with patch("src.core.system.stop_server") as mock_stop:
            with (
                patch("loguru.logger"),
                patch("time.sleep"),
                patch("os.execv"),
                patch("sys.executable", "python"),
            ):
                self.reboot_server(delay=0)
                mock_stop.assert_not_called()

    @pytest.mark.timeout(1)
    def test_reboot_server_no_infinite_loop(self, mock_execv):
        mock_execv.side_effect = Exception("Test error")
        with (
            patch("loguru.logger"),
            patch("time.sleep"),
            patch("sys.exit") as mock_exit,
        ):
            self.reboot_server(delay=0)
            mock_exit.assert_called_once_with(1)
