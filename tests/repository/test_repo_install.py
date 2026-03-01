import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import select
from src.database.models.model_configs import Configs
from src.database.repository import repo_default

from src.database.repository.repo_install import install_db


@pytest.fixture
def mock_install_deps():
    with (
        patch("src.core.config.config_create") as m_cfg,
        patch("src.database.engine.init_db") as m_init,
        patch("src.database.repository.repo_default.create_default_users"),
        patch("src.database.repository.repo_default.create_default_config"),
    ):
        yield {"config": m_cfg, "init": m_init}


def test_install_db_success(db_session, mock_install_deps):
    db_session.add_all(
        [
            Configs(name="app_port", value="0", about="port", input_format="number"),
            Configs(
                name="front_status",
                value="False",
                about="status",
                input_format="boolean",
            ),
        ]
    )
    db_session.commit()
    with patch("src.database.engine.SessionLocal") as mock_session_factory:
        mock_session_factory.return_value.__enter__.return_value = db_session
        params = {
            "app_port": 9000,
            "front": True,
            "sql_driver": "sqlite",
            "db_path": "/tmp/test",
        }
        result = install_db(**params)
        assert result["code"] == 201
        assert result["result"] is True
        mock_install_deps["config"].assert_called_once_with(
            data={"sql_driver": "sqlite", "db_path": "/tmp/test"}
        )
        port_val = db_session.scalar(
            select(Configs.value).where(Configs.name == "app_port")
        )
        front_val = db_session.scalar(
            select(Configs.value).where(Configs.name == "front_status")
        )
        assert port_val == "9000"
        assert front_val in ["True", "1"]


def test_install_db_exception(db_session, mock_install_deps):
    with patch("src.database.engine.SessionLocal") as mock_session_factory:
        mock_session = mock_session_factory.return_value.__enter__.return_value
        mock_session.execute.side_effect = Exception("SQL Crash")
        result = install_db(app_port=80, front=False)
        assert result["code"] == 500
        assert "SQL Crash" in result["message"]
        assert result["result"] is False
