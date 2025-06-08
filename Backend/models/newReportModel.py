from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime
from bson import ObjectId
from enum import Enum
from models.base import PyObjectId

class CellType(str, Enum):
    STRING = "string"
    DECIMAL = "decimal"
    BOOLEAN = "boolean"

class TableCell(BaseModel):
    value: Union[str, float, bool]
    cell_type: CellType

class TableRow(BaseModel):
    row: str
    col: str
    value: Union[str, float, bool]

class TableResponse(BaseModel):
    table: List[TableRow]

class QuestionResponse(BaseModel):
    """Base model for question responses"""
    string_value: Optional[str] = None
    decimal_value: Optional[float] = None
    bool_value: Optional[bool] = None
    link: Optional[str] = None
    note: Optional[str] = None
    table: Optional[Dict] = None

class UpdateLog(BaseModel):
    question_id: str
    updated_by: str
    updated_at: datetime
    previous_value: Optional[str] = None
    new_value: Optional[str] = None

class CreateReportRequest(BaseModel):
    """Model for creating a new report"""
    company_id: str
    plant_id: str
    financial_year: str

class QuestionUpdate(BaseModel):
    """Model for updating a question's response"""
    question_id: str
    response: Dict

class Report(BaseModel):
    """Model for a complete report"""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str
    plant_id: str
    financial_year: str
    responses: Dict[str, Dict] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    last_modified_at: Optional[datetime] = None
    last_modified_by: Optional[str] = None
    updates: Optional[List[UpdateLog]] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        allow_population_by_field_name = True