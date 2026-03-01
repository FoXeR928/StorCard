from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal


class InstallSchemas(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
        json_schema_extra={
            "example": {
                "app_port": 7000,
                "sql_driver": "sqlite",
                "sql_db": "storcard_db",
                "db_path": "./instance",
                "front": True,
            }
        },
    )

    app_port: int = Field(7000, ge=1, le=65535)
    sql_driver: Literal["sqlite", "mysql", "postgresql"]
    sql_host: Optional[str] = None
    sql_port: Optional[int] = Field(None, ge=1, le=65535)
    sql_db: str = Field("storcard_db", min_length=1)
    sql_user: Optional[str] = None
    sql_password: Optional[str] = None
    db_path: Optional[str] = Field("./data", min_length=1)
    front_status: bool = True
