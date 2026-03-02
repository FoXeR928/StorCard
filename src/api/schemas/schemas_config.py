from pydantic import BaseModel
from typing import Any


class ConfigUpdate(BaseModel):
    name: str
    value: Any
