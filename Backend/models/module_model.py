from typing import List, Optional, Union
from pydantic import BaseModel, Field, constr
from datetime import datetime
import uuid
from enum import Enum

class QuestionType(str, Enum):
    TABLE = "table"
    SUBJECTIVE = "subjective"

class SubjectiveType(str, Enum):
    STRING = "string"         # For text/string inputs
    INTEGER = "integer"       # For whole numbers
    FLOAT = "float"          # For decimal numbers
    BOOLEAN = "boolean"      # For yes/no inputs
   

class Question(BaseModel):
    question_id: str = Field(...)  # Format: Q1_P8, Q24_A etc.
    question: str = Field(...)     # The actual question text
    type: QuestionType = Field(...) # table or subjective
    subjective_type: Optional[SubjectiveType] = None  # Required if type is subjective
    is_required: bool = Field(default=True)  # Whether the question is mandatory
    link: Optional[str] = None     # Optional link
    note: Optional[str] = None     # Optional additional note

class QuestionCategory(BaseModel):
    category_name: str = Field(...)
    questions: List[Question] = Field(default_factory=list)

class SubModule(BaseModel):
    submodule_name: str = Field(...)
    question_categories: List[QuestionCategory] = Field(default_factory=list)

class Module(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str = Field(...)  # References company_collection
    plant_id: str = Field(...)    # References plants_collection
    financial_year: str = Field(...) # Format: YYYY_YYYY (e.g. 2024_2025)
    module_name: str = Field(...)
    submodules: List[SubModule] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ModuleCollection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str = Field(...)  # References company_collection
    plant_id: str = Field(...)    # References plants_collection
    financial_year: str = Field(...) # Format: YYYY_YYYY (e.g. 2024_2025)
    modules: List[Module] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None 