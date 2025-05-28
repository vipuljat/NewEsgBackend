from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict
from models.base import PyObjectId
from datetime import datetime

class UpdateLog(BaseModel):
    question_id: str
    updated_by: str
    updated_at: datetime
    schema_path: str
    previous_value: Optional[str] = None  # To track previous value for +1/-1 logic
    new_value: Optional[str] = None  # To track new value for +1/-1 logic

class PlantManager(BaseModel):
    name: str
    employee_id: str
    contact_email: EmailStr
    contact_phone: str

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Location(BaseModel):
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    coordinates: Optional[Coordinates] = None

class OperationLocations(BaseModel):
    plants: int
    offices: int
    total: int

class MarketsServed(BaseModel):
    national: Optional[int] = None  # No. of States
    international: Optional[int] = None  # No. of Countries

class SectionProgress(BaseModel):
    total_questions: int
    answered_questions: int


class PrincipleProgress(BaseModel):
    principle_1: SectionProgress
    principle_2: SectionProgress
    principle_3: SectionProgress
    principle_4: SectionProgress
    principle_5: SectionProgress
    principle_6: SectionProgress
    principle_7: SectionProgress
    principle_8: SectionProgress
    principle_9: SectionProgress

class SectionCProgress(BaseModel):
    total: SectionProgress
    principles: PrincipleProgress

class ModuleSubSectionProgress(BaseModel):
    total_questions: int
    answered_questions: int

class HRModule(BaseModel):
    workforce_details: ModuleSubSectionProgress
    employee_wellbeing: ModuleSubSectionProgress
    human_rights: ModuleSubSectionProgress
    retirement: ModuleSubSectionProgress
    others: ModuleSubSectionProgress

class LegalModule(BaseModel):
    policy_and_governance: ModuleSubSectionProgress
    ethical_conduct: ModuleSubSectionProgress
    policy_advocacy: ModuleSubSectionProgress
    others: ModuleSubSectionProgress

class FinanceModule(BaseModel):
    products_and_services: ModuleSubSectionProgress
    csr: ModuleSubSectionProgress
    inclusive_growth: ModuleSubSectionProgress
    transparency_and_governance: ModuleSubSectionProgress
    consumer_responsibility: ModuleSubSectionProgress

class AdminModule(BaseModel):
    entity_details: ModuleSubSectionProgress
    operations: ModuleSubSectionProgress
    corporate_structure: ModuleSubSectionProgress
    stakeholder_engagement: ModuleSubSectionProgress

class EnvironmentModule(BaseModel):
    sustainable_products: ModuleSubSectionProgress
    energy_emission: ModuleSubSectionProgress
    water_and_waste: ModuleSubSectionProgress
    environmental_compliance: ModuleSubSectionProgress

class ModulesProgress(BaseModel):
    workforce: HRModule
    legal: LegalModule
    finance: FinanceModule
    admin: AdminModule
    environment: EnvironmentModule

class SectionAProgress(BaseModel):
    entity_details: ModuleSubSectionProgress
    stock_and_subsidiaries: ModuleSubSectionProgress
    products_and_operations: ModuleSubSectionProgress
    csr_and_governance: ModuleSubSectionProgress
    employees: ModuleSubSectionProgress
    total: SectionProgress

class SectionBProgress(BaseModel):
    policy_and_governance: ModuleSubSectionProgress
    others: ModuleSubSectionProgress
    total: SectionProgress

class Progress(BaseModel):
    section_a: SectionAProgress
    section_b: SectionBProgress
    section_c: SectionCProgress
    modules: ModulesProgress

class Plant(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    plant_id: str
    plant_name: str
    company_id: str
    plant_manager: Optional[PlantManager] = None
    location: Optional[Location] = None
    operational_status: Optional[str] = None
    establishment_date: Optional[datetime] = None
    financial_year: Optional[str] = None
    operation_locations: Optional[Dict[str, OperationLocations]] = None
    markets_served: Optional[MarketsServed] = None
    export_contribution: Optional[float] = None
    customer_types: Optional[str] = None
    section_progress: Progress
    created_at: datetime
    updated_at: Optional[datetime] = None
    updates: Optional[List[UpdateLog]] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }