from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
from datetime import datetime
from models.base import PyObjectId

class PlantManager(BaseModel):
    name: str
    employee_id: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    user_role: str

class Employee(BaseModel):
    employee_id: str
    name: str
    email: EmailStr
    password: str
    department: str
    user_role: List[str]  # e.g., "hr", "admin", "staff"

class PlantEmployee(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str
    plant_id: str
    financial_year: str
    plant_manager: Optional[PlantManager] = None
    employees: List[Employee] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
    

class InitializePlantRequest(BaseModel):
    company_id: str
    plant_id: str
    financial_year: str
    plant_manager: PlantManager


class UpdateEmployeeRolesRequest(BaseModel):
    employee_id: str  # Can also use email for lookup
    roles: List[str]  # Roles to append to user_role