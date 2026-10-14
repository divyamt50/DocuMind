import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class DocumentCreate(BaseModel):
    file_name:str = Field(min_length=1, max_length=255)
    s3_key:str = Field(min_length=1, max_length=255)

class DocumentUpdate(BaseModel):
    file_name:str|None = Field(default=None, min_length=1, max_length=255)



class DocumentChunkRead(BaseModel):
    id:uuid.UUID
    chunk_index:int
    content:str
    created_at:datetime
    modified_at:datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentRead(BaseModel):
    id:uuid.UUID
    tenant_id:uuid.UUID
    file_name:str
    s3_key:str
    status:str
    created_at:datetime
    modified_at:datetime
    chunks:list[DocumentChunkRead] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class DocumentListResponse(BaseModel):
    items:list[DocumentRead]
    total:int
    limit:int
    offset:int