from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class TableColumnHeader(BaseModel):
    label: str  # Top-level label for the column group
    headers: Optional[List[str]] = None  # Direct column headers under the label
    sub_headers: Optional[List[str]] = None  # Sub-headers under each header
    min_width: Optional[int] = None  # Minimum column width (characters)
    max_width: Optional[int] = None  # Maximum column width (characters)
    type: Optional[str] = None  # Data type (e.g., 'number', 'string', 'date')
    calc_formula: Optional[str] = None  # For special calc columns
    special: Optional[bool] = False  # Is this a special/calc column?

class TableRowDefinition(BaseModel):
    name: str  # Row name or definition
    type: Optional[str] = None  # Data type or special type (e.g., 'calc_row')
    calc_formula: Optional[str] = None  # For special calc rows
    special: Optional[bool] = False  # Is this a special/calc row?

class TableQuestionMeta(BaseModel):
    question_id: str
    description: Optional[str] = None
    columns: List[TableColumnHeader]  # Hierarchical column definitions
    rows: List[TableRowDefinition]  # Predefined row definitions (metadata)
    min_col_width: Optional[int] = None
    max_col_width: Optional[int] = None
    char_limit: Optional[int] = None  # For wrapping header content
    restrictions: Optional[Dict[str, Any]] = None  # Any additional rules

# New model for submitted table responses
class TableCellResponse(BaseModel):
    row_id: str
    col_id: str
    value: Any  # Can be string, number, boolean, etc., based on column type
    calc: Optional[bool] = False
    note: Optional[str] = None

class TableRowResponse(BaseModel):
    row_id: str
    cells: List[TableCellResponse]
    calc: Optional[bool] = False
    note: Optional[str] = None

class TableQuestionResponse(BaseModel):
    question_id: str
    meta_version: Optional[str] = None
    rows: List[TableRowResponse]  # Dynamically added rows are allowed here
    last_updated: str
    updated_by: str
    notes: Optional[str] = None

# Example usage:
# meta = TableQuestionMeta(
#     question_id="Q1",
#     description="Sample table question",
#     columns=[
#         TableColumnHeader(label="Main Label", headers=["Header1", "Header2"], min_width=10, max_width=20, type="number"),
#         TableColumnHeader(label="Calc", special=True, calc_formula="Header1 + Header2")
#     ],
#     rows=[
#         TableRowDefinition(name="Row1", type="number"),
#         TableRowDefinition(name="Total", type="calc_row", special=True, calc_formula="sum")
#     ],
#     min_col_width=8,
#     max_col_width=25,
#     char_limit=15
# )
#
# response = TableQuestionResponse(
#     question_id="Q1",
#     meta_version="1.0",
#     rows=[
#         TableRowResponse(
#             row_id="row1",
#             cells=[
#                 TableCellResponse(row_id="row1", col_id="Header1", value=10),
#                 TableCellResponse(row_id="row1", col_id="Header2", value=20)
#             ]
#         ),
#         # Dynamically added row from frontend
#         TableRowResponse(
#             row_id="row2",
#             cells=[
#                 TableCellResponse(row_id="row2", col_id="Header1", value=15),
#                 TableCellResponse(row_id="row2", col_id="Header2", value=25)
#             ]
#         )
#     ],
#     last_updated="2025-06-08T18:59:00",
#     updated_by="user123"
# )