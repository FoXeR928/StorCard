class SyncItemShem(BaseModel):
    id: UUID
    name: Optional[str]=None
    about: Optional[str]=None
    image: Optional[str]=None
    own_login: str
    version: int
    is_deleted:Optional[bool]=None
    code: Optional[str]=None
    code_type: Optional[str] = None

class SyncShem(Base):
    changes:List[SyncItem]
