from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from models.base import PyObjectId
from datetime import datetime



class ContactPerson(BaseModel):
    name: str
    telephone: str
    email: EmailStr

class HoldingSubsidiaryAssociate(BaseModel):
    name: str
    type: str  # e.g., "Subsidiary", "Holding", "Associate", "Joint Venture"
    percentage_shares_held: float
    participates_in_brsr: bool

class Company(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str  # Q1: CIN
    name: str  # Q2: Name
    year_of_incorporation: int  # Q3: Year of Incorporation
    registered_office_address: str  # Q4: Registered Office
    corporate_address: str  # Q5: Corporate Address
    email: EmailStr  # Q6: E-mail
    telephone: str  # Q7: Telephone
    website: str  # Q8: Website
    financial_year: str  # Q9: Financial Year (e.g., "2024-2025")
    stock_exchanges: List[str]  # Q10: Stock Exchange(s)
    paid_up_capital_inr: float  # Q11: Paid-up Capital
    contact_person: ContactPerson  # Q12: Contact Person
    reporting_boundary: str  # Q13: Reporting Boundary (Standalone/Consolidated)
    holding_subsidiary_associate_companies: List[HoldingSubsidiaryAssociate]  # Q21a: Company Details
    plants: List[str]  # List of plant_ids
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }