from typing import Any, Optional


def api_response(
    success: bool,
    message: str,
    code: int = 200,
    category: Optional[str] = None,
    **extra_data: Any,
) -> dict:
    return {
        "result": success,
        "message": message,
        "category": category or ("success" if success else "error"),
        "code": code,
        **extra_data,
    }


def error_404(msg: str = "Ресурс не найден"):
    return api_response(False, msg, 404, "warning")


def error_500(msg: str = "Ошибка сервера"):
    return api_response(False, msg, 500, "error")


def error_403(msg: str = "Доступ запрещен"):
    return api_response(False, msg, 403, "warning")

def error_401(msg: str = "Авторизация не пройдена"):
    return api_response(False, msg, 401, "warning")
