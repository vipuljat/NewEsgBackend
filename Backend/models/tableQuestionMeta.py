# Table Question Metadata Model
# This model defines the structure and rules for table-type questions.

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
    rows: List[TableRowDefinition]  # Row definitions
    min_col_width: Optional[int] = None
    max_col_width: Optional[int] = None
    char_limit: Optional[int] = None  # For wrapping header content
    restrictions: Optional[Dict[str, Any]] = None  # Any additional rules

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
