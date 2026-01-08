from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional

class SSHCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    host: str = Field(..., min_length=1, max_length=255)
    port: int = Field(..., gt=0, le=65535)
    username: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=255)
    
    @field_validator("name", "host", "username", "password", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        """Удаляет пробелы в начале и конце строк"""
        if isinstance(v, str):
            return v.strip()
        return v
    
    @field_validator("name", "host", "username", mode="after")
    @classmethod
    def validate_not_empty_after_strip(cls, v):
        """Проверяет, что поле не пусто после удаления пробелов"""
        if not v or not v.strip():
            raise ValueError("Поле не может быть пустым")
        return v

class SSHCreateResponse(BaseModel):

    id: int
    name: str
    host: str
    port: int
    username: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
    
class SSHUpdateRequest(BaseModel):
    name: str = Field(None, min_length=1, max_length=100)
    host: str = Field(None, min_length=1, max_length=255)
    port: int = Field(None, gt=0, le=65535)
    username: str = Field(None, min_length=1, max_length=100)
    password: str = Field(None, min_length=1, max_length=255)