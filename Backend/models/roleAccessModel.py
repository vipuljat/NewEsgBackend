from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from models.base import PyObjectId
from datetime import datetime


class ModuleAccessRequest(BaseModel):
    user_role: str
    company_id: str
    plant_id: str
    financial_year: str

class UpdatePermissionsRequest(BaseModel):
    employee_name: str
    employee_email: str
    roles : List[str]  # List of role IDs to grant access to


class Role(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str
    role_name: str  # e.g., "hr", "it", "marketing"
    role_id: str
    created_by: str  # Admin user ID or email
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class RoleAccess(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str
    plant_id: Optional[str] = None  # None for company-level questions
    financial_year: str  # e.g., "2024-25"
    question_id: str  # e.g., "Q1", "B_Q1b", "C_P6_Q1"
    role_permissions: Dict[str, bool]  # e.g., {"hr": True, "it": False, "marketing": True}
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }