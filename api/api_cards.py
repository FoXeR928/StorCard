from pathlib import Path
from typing import Optional
from loguru import logger
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from pydantic import BaseModel

from api.api_auth import get_current_user, UserSchema
from db.db_cards import CardRepository

cards_app = APIRouter(prefix="/cards", tags=["Карты"])

MEDIA_DIR = Path("/app/data/media")


class AddCardSchema(BaseModel):
    name: str
    about: Optional[str] = None
    barcode: str 


class UpdateCardSchema(BaseModel):
    name: Optional[str] = None
    about: Optional[str] = None
    barcode: Optional[str] = None


class ShareAccessSchema(BaseModel):
    target_login: str
    access_level: str 


class ChangeOwnerSchema(BaseModel):
    target_login: str

@cards_app.get("/", summary="Получение личных карт текущего пользователя")
async def get_my_cards(current_user: UserSchema = Depends(get_current_user)):
    """Возвращает список карт, к которым у текущего авторизованного пользователя есть доступ."""
    return CardRepository.get_cards(current_user=current_user, global_view=False)


@cards_app.get("/all", summary="Получение ВСЕХ карт в базе данных (Только для глобального Администратора)")
async def get_all_cards(current_user: UserSchema = Depends(get_current_user)):
    """Доступно только пользователям с флагом is_admin=True."""
    return CardRepository.get_cards(current_user=current_user, global_view=True)


@cards_app.get("/{card_id}", summary="Получение детальной информации о конкретной карте")
async def get_card_by_id(card_id: str, current_user: UserSchema = Depends(get_current_user)):
    return CardRepository.get_card_detail(card_id=card_id, current_user=current_user)


@cards_app.post("/", status_code=status.HTTP_201_CREATED, summary="Создание новой дисконтной карты")
async def create_card(card_data: AddCardSchema, current_user: UserSchema = Depends(get_current_user)):
    return CardRepository.add_card(
        name=card_data.name,
        about=card_data.about,
        barcode=card_data.barcode,
        current_user=current_user
    )


@cards_app.patch("/{card_id}", summary="Универсальное обновление текстовых параметров карты")
async def update_card_fields(
    card_id: str, 
    update_data: UpdateCardSchema, 
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Позволяет обновить имя, описание или штрихкод карты в любом сочетании.
    Доступно пользователям с уровнем прав 'owner' или 'editor'.
    """
    return CardRepository.update_card(
        card_id=card_id,
        update_data=update_data.model_dump(),
        current_user=current_user
    )


@cards_app.post("/{card_id}/share", status_code=status.HTTP_201_CREATED, summary="Предоставление доступа к карте другому пользователю")
async def share_card(
    card_id: str, 
    share_data: ShareAccessSchema, 
    current_user: UserSchema = Depends(get_current_user)
):
    """Позволяет владельцу карты поделиться ей, выдав права 'editor' или 'viewer' по логину."""
    return CardRepository.share_card_access(
        card_id=card_id,
        target_login=share_data.target_login,
        access_level=share_data.access_level,
        current_user=current_user
    )


@cards_app.put("/{card_id}/owner", summary="Передача прав главного владельца карты")
async def change_owner(
    card_id: str, 
    owner_data: ChangeOwnerSchema, 
    current_user: UserSchema = Depends(get_current_user)
):
    """Только текущий 'owner' карты может полностью передать права владения другому пользователю."""
    return CardRepository.change_card_owner(
        card_id=card_id,
        target_login=owner_data.target_login,
        current_user=current_user
    )


@cards_app.put("/{card_id}/image", summary="Загрузка или обновление изображения лицевой/оборотной стороны карты")
async def upload_card_image(
    card_id: str, 
    file: UploadFile = File(...), 
    current_user: UserSchema = Depends(get_current_user)
):
    """
    Принимает файл изображения, физически сохраняет его на сервере в папку /app/data/media/
    и записывает относительный путь в базу данных вместо тяжелого BLOB-объекта.
    """
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    
    file_extension = Path(file.filename).suffix
    if file_extension.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Разрешены только файлы изображений формата: JPG, PNG, WEBP."
        )

    local_file_name = f"{card_id}{file_extension}"
    full_save_path = MEDIA_DIR / local_file_name
    relative_db_path = f"media/{local_file_name}"

    try:
        with open(full_save_path, "wb") as buffer:
            buffer.write(await file.read())
            
        return CardRepository.update_card(
            card_id=card_id,
            update_data={"image_path": relative_db_path},
            current_user=current_user
        )
    except Exception as err:
        logger.error(f"Ошибка при физическом сохранении файла на сервере: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось сохранить изображение на сервере."
        )


@cards_app.delete("/{card_id}", summary="Полное удаление дисконтной карты из системы")
async def delete_card(card_id: str, current_user: UserSchema = Depends(get_current_user)):
    """Полностью удаляет саму карту и каскадно очищает таблицу прав доступа к ней."""
    return CardRepository.delete_card(card_id=card_id, current_user=current_user)
