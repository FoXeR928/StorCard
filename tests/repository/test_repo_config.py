import pytest
from unittest.mock import MagicMock, patch
from src.database.repository.repo_config import (
    get_all_configs_dict,
    get_config_val,
    update_config_query,
)

MOCK_DATA = [
    MagicMock(name="skey", value="secret123"),
    MagicMock(name="short_token", value="3600"),
]


@patch("src.database.engine.SessionLocal")
def test_get_all_configs_logic(mock_session_factory):
    mock_session = mock_session_factory.return_value.__enter__.return_value
    mock_row_1 = MagicMock()
    mock_row_1.name = "skey"
    mock_row_1.value = "secret123"
    mock_row_2 = MagicMock()
    mock_row_2.name = "short_token"
    mock_row_2.value = "3600"
    mock_session.execute.return_value.all.return_value = [mock_row_1, mock_row_2]
    get_all_configs_dict.cache_clear()
    res = get_all_configs_dict()
    assert res["skey"] == "secret123"
    assert len(res) == 2
    assert mock_session.execute.call_count == 1


@patch("src.database.engine.SessionLocal")
def test_update_and_cache_clear(mock_session_factory):
    mock_session = mock_session_factory.return_value.__enter__.return_value
    mock_result = MagicMock()
    mock_result.rowcount = 1
    response = update_config_query("skey", "new_secret")
    assert response["result"] is True
    assert "обновлен" in response["message"]
    mock_session.commit.assert_called_once()


def test_get_config_val_fallback():
    val = get_config_val("non_existent_key", default="fallback")
    assert val == "fallback"
