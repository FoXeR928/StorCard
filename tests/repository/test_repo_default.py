import pytest
from unittest.mock import patch
from sqlalchemy import select, func
from src.database.models.model_users import Users
from src.database.models.model_configs import Configs

from src.database.repository.repo_default import (
    create_default_users,
    create_default_config,
)


@pytest.fixture(autouse=True)
def mock_session_factory(db_session):
    with patch("src.database.engine.SessionLocal") as mocked:
        mocked.return_value.__enter__.return_value = db_session
        yield mocked


def test_create_users_first_run(db_session):
    create_default_users(admin_login="boss", admin_password="123")
    user = db_session.scalar(select(Users).where(Users.login == "boss"))
    assert user is not None
    assert user.is_admin is True
    assert user.password_hash != "123"


def test_create_users_already_exists(db_session):
    db_session.add(Users(login="existing", is_admin=True, password_hash=b"dummy_hash"))
    db_session.commit()

    create_default_users(admin_login="new_admin")

    count = db_session.scalar(select(func.count(Users.id)))
    assert count == 1
    assert db_session.scalar(select(Users.login)) == "existing"


def test_create_users_recreate(db_session):
    db_session.add(Users(login="old_user", is_admin=False, password_hash=b"dummy_hash"))
    db_session.commit()

    create_default_users(recreate=True, admin_login="new_admin")

    users = db_session.scalars(select(Users)).all()
    assert len(users) == 1
    assert users[0].login == "new_admin"


def test_create_config_full_set(db_session):
    create_default_config()

    count = db_session.scalar(select(func.count(Configs.id)))
    assert count == 8

    skey = db_session.scalar(select(Configs.value).where(Configs.name == "skey"))
    assert len(skey) > 32


def test_create_config_partial_exists(db_session):
    db_session.add(
        Configs(
            name="app_port",
            value="9999",
            about="Порт приложения",
            input_format="number",
        )
    )
    db_session.commit()

    create_default_config()
    port = db_session.scalar(select(Configs.value).where(Configs.name == "app_port"))
    assert port == "9999"
    about = db_session.scalar(select(Configs.about).where(Configs.name == "app_port"))
    assert about == "Порт приложения"
    input_format = db_session.scalar(
        select(Configs.input_format).where(Configs.name == "app_port")
    )
    assert input_format == "number"
    count = db_session.scalar(select(func.count(Configs.id)))
    assert count == 8


@patch("src.core.system.stop_server")
def test_create_config_error_calls_stop(mock_stop, db_session):
    with patch("sqlalchemy.orm.Session.add_all", side_effect=Exception("Crash")):
        create_default_config()
        mock_stop.assert_called_once_with(1)
