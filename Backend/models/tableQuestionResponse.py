# TableQuestionResponse: Response structure for table-type questions
# This is analogous to the TableQuestionMeta, but for storing/fetching user responses.

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel

class TableCellResponse(BaseModel):
    row_id: str  # Unique identifier for the row
    col_id: str  # Unique identifier for the column
    value: Union[str, float, bool, None]  # The value entered/selected
    calc: Optional[bool] = False  # Is this a calculated cell?
    note: Optional[str] = None  # Any note or comment for this cell

class TableRowResponse(BaseModel):
    row_id: str
    cells: List[TableCellResponse]
    calc: Optional[bool] = False  # Is this a calculated row?
    note: Optional[str] = None

class TableColumnResponse(BaseModel):
    col_id: str  # Unique identifier for the column
    label: Optional[str] = None  # Display label for the column
    type: Optional[str] = None  # Data type (e.g., 'number', 'string', 'date')
    calc: Optional[bool] = False  # Is this a calculated column?
    note: Optional[str] = None  # Any note or comment for this column

class TableQuestionResponse(BaseModel):
    question_id: str
    columns: List[TableColumnResponse]  # Explicit column info for renderer
    rows: List[TableRowResponse]
    meta_version: Optional[str] = None  # To track which meta version this response is for
    last_updated: Optional[str] = None
    updated_by: Optional[str] = None
    notes: Optional[str] = None  # General notes for the table
    # You can add more fields as needed for audit, status, etc.

# This structure is designed to be flexible and extensible for complex table-type questions.
