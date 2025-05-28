from pydantic import BaseModel, Field, validator
from typing import Optional, Dict
from models.base import PyObjectId
from datetime import datetime

class Role(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str
    role_name: str  # e.g., "hr", "it", "marketing"
    role_id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

class RoleAccess(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str
    plant_id: Optional[str] = None
    financial_year: str
    question_id: str
    role_permissions: Dict[str, bool]
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator("role_permissions")
    def validate_role_permissions(cls, v):
        # Ensure all keys are valid role names (optional: validate against roles_collection)
        if not v:
            raise ValueError("role_permissions cannot be empty")
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }