import pytest
from unittest.mock import patch, MagicMock

INSTALL_URL = "/install"


@pytest.fixture
def mock_repo_install():
    with patch("src.database.repository.repo_install.install_db") as mocked:
        yield mocked


@pytest.fixture
def mock_system():
    with patch("src.core.system.reboot_server") as mocked:
        yield mocked


def test_api_install_success(client, mock_repo_install, mock_system):
    mock_repo_install.return_value = {"result": True, "message": "Success", "code": 201}
    payload = {
        "app_port": 8080,
        "sql_driver": "sqlite",
        "sql_db": "test",
        "db_path": "./data",
        "front_status": True,
    }
    response = client.post(INSTALL_URL, json=payload)
    assert response.status_code == 201
    assert response.json()["result"] is True
    mock_repo_install.assert_called_once()
    mock_system.assert_called_once_with(delay=2)


def test_api_install_fail(client, mock_repo_install, mock_system):
    mock_repo_install.return_value = {
        "result": False,
        "message": "Database Error",
        "code": 500,
    }

    payload = {
        "app_port": 8080,
        "sql_driver": "sqlite",
        "sql_db": "test",
        "db_path": "./data",
        "front_status": True,
    }
    response = client.post(INSTALL_URL, json=payload)
    assert response.status_code == 500
    assert response.json()["result"] is False
    mock_system.assert_not_called()


def test_api_install_validation_error(client):
    payload = {"app_port": "not_a_number", "sql_driver": "sqlite"}
    response = client.post(INSTALL_URL, json=payload)
    assert response.status_code == 422
