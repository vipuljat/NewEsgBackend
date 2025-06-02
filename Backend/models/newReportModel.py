from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List, Union
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
    string_value: Optional[str] = None
    bool_value: Optional[bool] = None
    decimal_value: Optional[float] = None
    link: Optional[str] = None
    note: Optional[str] = None
    table: Optional[List[TableRow]] = None

class UpdateLog(BaseModel):
    question_id: str
    updated_by: str
    updated_at: datetime
    previous_value: Optional[str] = None
    new_value: Optional[str] = None

class CreateReportRequest(BaseModel):
    company_id: str
    plant_id: str
    financial_year: str

class QuestionUpdate(BaseModel):
    question_id: str
    response: Optional[Union[QuestionResponse, TableResponse]] = None

class Report(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str
    plant_id: Optional[str] = None
    financial_year: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    responses: Dict[str, Union[QuestionResponse, TableResponse]] = {}
    updates: Optional[List[UpdateLog]] = None
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        allow_population_by_field_name = True