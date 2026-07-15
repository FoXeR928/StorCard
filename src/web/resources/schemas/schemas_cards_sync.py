import uuid
from typing import Optional, List
from pydantic import BaseModel


class SyncItemShem(BaseModel):
    id: uuid.UUID
    name: str
    about: Optional[str] = None
    image: Optional[str] = None
    own_login: str
    version: int
    is_deleted: bool
    code: str
    code_type: str


class UpstreamSyncShem(BaseModel):
    changes: List[SyncItemShem]


class DownstreamSyncResponse(BaseModel):
    changes: List[SyncItemShem]
    current_server_version: int
    has_more: bool