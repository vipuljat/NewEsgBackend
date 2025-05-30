from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class UpdateLog(BaseModel):
    question_id: str
    updated_by: str
    updated_at: datetime
    previous_value: Optional[str] = None
    new_value: Optional[str] = None

class AuditLog(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")  # Use string for serialization
    company_id: str
    plant_id: Optional[str] = None
    financial_year: str
    updates: Optional[List[UpdateLog]] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,  # Convert ObjectId to string during serialization
            datetime: lambda v: v.isoformat()
        }