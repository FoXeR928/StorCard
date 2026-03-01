import pytest
from unittest.mock import patch, MagicMock
import src.core.system as system


def test_stop_server_calls_exit():
    with patch("src.core.system.stop_server", wraps=system.stop_server):
        with pytest.raises(SystemExit) as excinfo:
            system.stop_server(status=1)
        assert excinfo.value.code == 1


@patch("os.execv")
@patch("time.sleep")
def test_reboot_server_calls_execv(mock_sleep, mock_execv):
    with patch("src.core.system.reboot_server", wraps=system.reboot_server):
        system.reboot_server(delay=0)
        mock_execv.assert_called_once()


@patch("os.execv")
@patch("src.core.system.sys.exit")
def test_reboot_server_failure(mock_exit, mock_execv):
    with patch("src.core.system.reboot_server", wraps=system.reboot_server):
        mock_execv.side_effect = OSError("Access denied")
        system.reboot_server(delay=0)
        mock_exit.assert_called_once_with(1)
