import uuid
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class RegisterRequest(BaseModel):
    tenant_name:str = Field(min_length=2, max_length=255)
    name:str = Field(min_length=1, max_length=255)
    email: EmailStr
    password:str = Field(min_length=12, max_length=128)

class LoginRequest(BaseModel):
    email: EmailStr
    password:str = Field(min_length=1, max_length=128)

class UserResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    tenant_id:uuid.UUID

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"