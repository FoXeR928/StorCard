import uuid
from typing import Optional, List
from pydantic import BaseModel

class SyncItemShem(BaseModel):
    id: uuid.UUID
    name: Optional[str]=None
    about: Optional[str]=None
    image: Optional[str]=None
    own_login: str
    version: int
    is_deleted:Optional[bool]=None
    code: Optional[str]=None
    code_type: Optional[str] = None

class SyncShem(BaseModel):
    changes:List[SyncItemShem]
