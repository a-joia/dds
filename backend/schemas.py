from pydantic import BaseModel, Field as PydanticField
from typing import List, Optional, Dict, Any

class FieldBase(BaseModel):
    name: str
    meta: Optional[Dict[str, Any]] = {}

class FieldCreate(FieldBase):
    parent_id: Optional[int] = None

class FieldRead(FieldBase):
    id: int
    subfields: List['FieldRead'] = []
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

FieldRead.update_forward_refs()

class TableBase(BaseModel):
    name: str

class TableCreate(TableBase):
    pass

class TableRead(TableBase):
    id: int
    fields: List[FieldRead] = []
    class Config:
        from_attributes = True

class DatabaseBase(BaseModel):
    name: str

class DatabaseCreate(DatabaseBase):
    pass

class DatabaseRead(DatabaseBase):
    id: int
    tables: List[TableRead] = []
    class Config:
        from_attributes = True

class ClusterBase(BaseModel):
    name: str

class ClusterCreate(ClusterBase):
    pass

class ClusterRead(ClusterBase):
    id: int
    databases: List[DatabaseRead] = []
    class Config:
        from_attributes = True

class EdgeBase(BaseModel):
    from_field_id: int
    to_field_id: int
    type: str

class EdgeCreate(EdgeBase):
    pass

class EdgeRead(EdgeBase):
    id: int
    class Config:
        from_attributes = True 