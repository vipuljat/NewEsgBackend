from datetime import datetime
from fastapi import HTTPException
from typing import Dict, List
from database import role_access_collection

def normalize_financial_year(financial_year: str) -> str:
    """
    Normalize financial_year by replacing hyphens with underscores (e.g., '2024-2025' to '2024_2025').
    """
    return financial_year.replace("-", "_")

async def update_permissions(company_id: str, plant_id: str, financial_year: str, permissions_data: Dict, user_id: str) -> Dict[str, str]:
    """
    Update permissions for a company, plant, and financial year.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year (e.g., '2023-2024').
        permissions_data: Dictionary containing role_permissions.
        user_id: ID of the user performing the update.

    Returns:
        Dict with success message.

    Raises:
        HTTPException: If update fails.
    """
    try:
        permissions_data["company_id"] = company_id
        permissions_data["plant_id"] = plant_id
        permissions_data["financial_year"] = financial_year
        permissions_data["updated_at"] = datetime.utcnow()

        result = await role_access_collection.replace_one(
            {"company_id": company_id, "plant_id": plant_id, "financial_year": financial_year},
            permissions_data,
            upsert=True
        )
        if result.modified_count == 0 and result.upserted_id is None:
            raise HTTPException(status_code=500, detail="Failed to update permissions")

        return {"message": "Permissions updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update permissions: {str(e)}")

async def get_permissions(company_id: str, plant_id: str, financial_year: str) -> Dict:
    """
    Fetch permissions for a company, plant, and financial year.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year (e.g., '2023-2024').

    Returns:
        Permissions document.

    Raises:
        HTTPException: If permissions not found or fetch fails.
    """
    try:
        permissions = await role_access_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year
        })
        if not permissions:
            raise HTTPException(status_code=404, detail="Permissions not found")
        return permissions
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch permissions: {str(e)}")

async def check_module_access(
    company_id: str,
    plant_id: str,
    financial_year: str,
    user_role: str,
    module_name: str
) -> bool:
    """
    Check if a user role has access to a specific module.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2023-2024').
        user_role: Role of the user (e.g., 'hr', 'admin').
        module_name: Name of the module (e.g., 'workforce', 'compliance').

    Returns:
        Boolean indicating if the role has access to the module.

    Raises:
        HTTPException: If document, role, or module is not found.
    """
    valid_modules = {"workforce", "compliance", "environment", "finance", "EntityDetails"}
    if module_name not in valid_modules:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid module name: {module_name}. Valid modules are {valid_modules}"
        )

    doc = await role_access_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": financial_year
    })

    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"No permissions document found for company {company_id}, plant {plant_id}, financial year {financial_year}"
        )

    role_entry = next(
        (entry for entry in doc.get("role_permissions", []) if entry["role"] == user_role),
        None
    )

    if not role_entry:
        raise HTTPException(
            status_code=404,
            detail=f"Role {user_role} not found in permissions"
        )

    return role_entry["permissions"].get(module_name, False)