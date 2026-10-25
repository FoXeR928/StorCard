import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from loguru import logger

from api.api_auth import get_current_user
from core.crypto_utils import decrypt_storcard_file
from core.schemas import UserSchema
from db.db_migration import MIGRATION_VERSION, MigrationRepository

migration_app = APIRouter(prefix="/admin/migration", tags=["Миграция сервера"])

SUPPORTED_VERSIONS = (MIGRATION_VERSION,)


def _ensure_admin(current_user: UserSchema) -> None:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администратор может выполнять миграцию.",
        )


@migration_app.get(
    "/export",
    summary="Экспорт пользователей и карт (Только Админ)",
)
async def export_migration_data(
    current_user: UserSchema = Depends(get_current_user),
):
    """
    Возвращает plaintext JSON {version, users, cards}.
    Клиент сам шифрует его в AES-256 и сохраняет как .storcard.
    """
    _ensure_admin(current_user)
    try:
        return await MigrationRepository.export_all()
    except Exception as err:
        logger.exception(f"Ошибка экспорта миграции: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при экспорте данных.",
        )


@migration_app.post(
    "/import",
    summary="Импорт данных из защищенного файла .storcard",
)
async def import_migration_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    current_user: UserSchema = Depends(get_current_user),
):
    _ensure_admin(current_user)

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Пустой файл."
        )

    try:
        json_string = decrypt_storcard_file(password, file_bytes)
        data = json.loads(json_string)
    except Exception as err:
        logger.warning(f"Ошибка расшифровки файла миграции: {err}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный пароль или файл поврежден.",
        )

    if not isinstance(data, dict) or data.get("version") not in SUPPORTED_VERSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Несовместимая версия файла (поддерживаются: {SUPPORTED_VERSIONS}).",
        )

    try:
        return await MigrationRepository.import_data(data)
    except Exception as err:
        logger.exception(f"Ошибка при импорте данных: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка сервера при импорте данных.",
        )