from typing import List, Optional, Union
from pydantic import BaseModel, Field, constr
from datetime import datetime
import uuid
from enum import Enum
from pydantic import validator

class QuestionType(str, Enum):
    TABLE = "table"
    SUBJECTIVE = "subjective"

class StringMetadata(BaseModel):
    enabled: bool = Field(default=False)
    required: bool = Field(default=False)

class DecimalMetadata(BaseModel):
    enabled: bool = Field(default=False)
    required: bool = Field(default=False)

class BooleanMetadata(BaseModel):
    enabled: bool = Field(default=False)
    required: bool = Field(default=False)

class LinkMetadata(BaseModel):
    enabled: bool = Field(default=False)
    required: bool = Field(default=False)

class NoteMetadata(BaseModel):
    enabled: bool = Field(default=False)
    required: bool = Field(default=False)

class TableHeader(BaseModel):
    label: str  # Top-level header (column head)
    headers: Optional[List['TableHeader']] = None  # Nested headers (for multi-level headers)
    cell_type: Optional[str] = None  # Per-column data type (overrides global if set)
    required: Optional[bool] = None  # Is this column required?
    allowed_values: Optional[List[str]] = None  # For dropdown/select columns
    min_value: Optional[float] = None  # For numeric columns
    max_value: Optional[float] = None
    default_value: Optional[str] = None
    min_width: Optional[int] = None  # For UI rendering
    max_width: Optional[int] = None
    help_text: Optional[str] = None

class TableRow(BaseModel):
    name: str  # Row name/parameter
    required: bool = False
    allowed_values: Optional[List[str]] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    default_value: Optional[str] = None
    help_text: Optional[str] = None
    # Optionally, add more constraints here

class TableMetadata(BaseModel):
    headers: List[TableHeader]  # Hierarchical column headers
    rows: List[TableRow]        # Row definitions
    cell_type: Optional[str] = Field(None, description="Default data type for table cells: string, decimal, boolean, etc. (overridden by column)")
    min_col_width: Optional[int] = None
    max_col_width: Optional[int] = None
    horizontal_scroll_threshold: Optional[int] = None  # Number of columns before scroll
    # Optionally, add more constraints as needed

# Update forward references for TableHeader
TableHeader.update_forward_refs()

class Question(BaseModel):
    question_id: str = Field(...)  # Format: Q1_P8, Q24_A etc.
    question: str = Field(...)     # The actual question text
    type: QuestionType = Field(...) # table or subjective
    
    # Metadata flags for what type of data is expected/allowed
    has_string_value: bool = Field(default=False)  # Whether string input is expected
    has_decimal_value: bool = Field(default=False) # Whether decimal input is expected
    has_boolean_value: bool = Field(default=False) # Whether boolean input is expected
    has_link: bool = Field(default=False)         # Whether link input is expected
    has_note: bool = Field(default=False)         # Whether note input is expected
    
    # Required flags for each type of input
    string_value_required: bool = Field(default=False)
    decimal_value_required: bool = Field(default=False)
    boolean_value_required: bool = Field(default=False)
    link_required: bool = Field(default=False)
    note_required: bool = Field(default=False)

    table_metadata: Optional[TableMetadata] = None  # Only for table-type questions

    @validator('string_value_required')
    def validate_string_required(cls, v, values):
        if v and not values.get('has_string_value', False):
            raise ValueError('string_value_required cannot be True if has_string_value is False')
        return v

    @validator('decimal_value_required')
    def validate_decimal_required(cls, v, values):
        if v and not values.get('has_decimal_value', False):
            raise ValueError('decimal_value_required cannot be True if has_decimal_value is False')
        return v

    @validator('boolean_value_required')
    def validate_boolean_required(cls, v, values):
        if v and not values.get('has_boolean_value', False):
            raise ValueError('boolean_value_required cannot be True if has_boolean_value is False')
        return v

    @validator('link_required')
    def validate_link_required(cls, v, values):
        if v and not values.get('has_link', False):
            raise ValueError('link_required cannot be True if has_link is False')
        return v

    @validator('note_required')
    def validate_note_required(cls, v, values):
        if v and not values.get('has_note', False):
            raise ValueError('note_required cannot be True if has_note is False')
        return v

class QuestionCategory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    category_name: str = Field(...)
    questions: List[Question] = Field(default_factory=list)

class SubModule(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
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