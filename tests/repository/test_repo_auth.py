import pytest
from unittest.mock import patch
from src.database.models.model_users import Users
from src.database.repository.repo_auth import get_user_by_login, authenticate_user


@pytest.fixture(autouse=True)
def mock_session_factory(db_session):
    with patch("src.database.engine.SessionLocal") as mocked:
        mocked.return_value.__enter__.return_value = db_session
        yield mocked


def test_get_user_by_login_success(db_session):
    user = Users(login="test_user", user_name="Tester", is_admin=True)
    user.set_password("any_pass")
    db_session.add(user)
    db_session.commit()

    result = get_user_by_login("test_user")

    assert result is not None
    assert result.login == "test_user"
    assert result.user_name == "Tester"


def test_authenticate_user_success(db_session):
    """Успешная авторизация с генерацией токена."""
    user = Users(login="admin", user_name="Admin")
    user.set_password("secret_pass")
    db_session.add(user)
    db_session.commit()

    with patch("src.core.security.create_access_token", return_value="fake_jwt_token"):
        response = authenticate_user("admin", "secret_pass", long_session=False)

        assert response["result"] is True
        assert response["access_token"] == "fake_jwt_token"
        assert response["code"] == 200


def test_authenticate_user_wrong_password(db_session):
    """Отказ в доступе при неверном пароле."""
    user = Users(login="admin")
    user.set_password("correct_pass")
    db_session.add(user)
    db_session.commit()

    response = authenticate_user("admin", "wrong_password", long_session=False)

    assert response["result"] is False
    assert response["code"] == 401


def test_authenticate_user_not_found(db_session):
    """Пользователь не существует."""
    response = authenticate_user("ghost", "any_pass", long_session=True)

    assert response["result"] is False
    assert response["code"] == 401


@patch("src.core.security.create_access_token", return_value=None)
def test_authenticate_token_generation_fail(mock_token, db_session):
    """Ошибка, если токен не сгенерировался (вернул None или пустую строку)."""
    user = Users(login="admin")
    user.set_password("pass")
    db_session.add(user)
    db_session.commit()

    response = authenticate_user("admin", "pass", long_session=False)

    assert response["result"] is False
    assert response["code"] == 500
