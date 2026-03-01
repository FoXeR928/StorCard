import pytest
from src.core.responses import api_response, error_404


def test_api_response_structure():
    res = api_response(True, "OK", extra_field="test")
    assert res["result"] is True
    assert res["category"] == "success"
    assert res["extra_field"] == "test"


def test_api_response_error_category():
    res = api_response(False, "Fail")
    assert res["category"] == "error"


def test_error_404_shortcut():
    res = error_404("Missing")
    assert res["code"] == 404
    assert res["result"] is False
    assert res["category"] == "warning"
