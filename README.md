# StorCard

**StorCard** — self-hosted сервер для хранения и каталогизации скидочных и дисконтных карт.  
Работает через Docker, предоставляет REST API на FastAPI и поддерживает многопользовательский доступ с разграничением прав.

---

## 📱 Клиент

Официальное мобильное приложение — **StorCard Client** на Flutter:

**➡️ [github.com/FoXeR928/StorCard_client](https://github.com/FoXeR928/StorCard_client)**

---

## Возможности

- 🗂 **Хранение карт** — название, описание, штрихкод, изображение лицевой/оборотной стороны.
- 🔐 **JWT-авторизация** — OAuth2 Password Flow, access-токен Bearer + опциональный refresh-токен.
- 👥 **Разграничение прав**:
  - администратор системы (`is_admin`);
  - владелец карты (`owner`);
  - редактор (`editor`);
  - просмотрщик (`viewer`).
- 🤝 **Шеринг карт** между пользователями.
- 🔁 **Передача прав владельца** карты другому пользователю.
- 🖼 **Загрузка изображений** карт с хранением на диске (без BLOB в БД).
- 🧑‍💼 **Управление пользователями** — регистрация, смена пароля, роли, удаление.
- 🛡 **Защита от удаления последнего администратора**.
- 📦 **Миграция сервера** — перенос всех пользователей и карт на новое железо с сохранением паролей (v1.1.0).
- 🔒 **Шифрование миграции** — AES-256-CBC, пароль никогда не покидает клиент и не хранится в файле.
- 📝 **Логирование** в stdout и в ротируемый файл (loguru).
- 🐳 **Docker-first**: конфигурация через переменные окружения.
- 🗃 **Поддержка SQLite (по умолчанию) и PostgreSQL** через `DATABASE_URL`.
- ⚡ **Асинхронный доступ к БД** (SQLAlchemy 2 + aiosqlite/asyncpg).

---

## Быстрый старт (Docker)

### 1. Сборка образа

```bash
docker build -t storcard .
```

### 2. Запуск контейнера

```bash
docker run -d \
  --name storcard \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e ADMIN_LOGIN=admin \
  -e ADMIN_PASSWORD=change_me \
  -e DEBUG=true \
  storcard
```

Сервис будет доступен по адресу:

```
http://localhost:8000
```

Swagger UI (только при `DEBUG=true`):

```
http://localhost:8000/docs
```

> ⚠️ **Обязательно монтируйте `./data:/app/data`.**  
> В этой папке хранятся:
> - база данных SQLite (`storcard.db`);
> - секретный ключ JWT (`secret.key`) — при его потере все выданные токены станут недействительными;
> - загруженные изображения карт (`media/`);
> - логи (`logs/`).

---

## Docker Compose

```yaml
services:
  storcard:
    image: foxer928/storcard:latest
    container_name: storcard
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - storcard_data:/app/data
    environment:
      DEBUG: "false"
      APP_PORT: "8000"

volumes:
  storcard_data:
```

---
