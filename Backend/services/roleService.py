from fastapi import HTTPException
from typing import List
from database import role_access_collection

def normalize_financial_year(financial_year: str) -> str:
    """
    Normalize financial_year by replacing hyphens with underscores (e.g., '2024-2025' to '2024_2025').
    """
    return financial_year.replace("-", "_")

async def get_accessible_questions(
    company_id: str,
    plant_id: str,
    financial_year: str,
    user_role: str
) -> List[str]:
    """
    Fetch question IDs accessible to a specific role.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2024-2025').
        role_name: Role to query (e.g., 'hr', 'legal').

    Returns:
        List of question IDs where the role has access (permissions = true).

    Raises:
        HTTPException: If document or role is not found.
    """
    normalized_financial_year = normalize_financial_year(financial_year)
    
    # Find the role access document
    doc = await role_access_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"No role access document found for company {company_id}, "
                f"plant {plant_id}, financial year {financial_year}"
        )
    
    # Find the role's permissions
    role_entry = next(
        (entry for entry in doc.get("role_permissions", []) if entry["role"] == user_role),
        None
    )
    
    if not role_entry:
        raise HTTPException(
            status_code=404,
            detail=f"Role {user_role} not found in access permissions"
        )
    
    # Extract questions with true permissions
    accessible_questions = [
        question_id
        for question_id, has_access in role_entry["permissions"].items()
        if has_access
    ]
    
    return accessible_questions