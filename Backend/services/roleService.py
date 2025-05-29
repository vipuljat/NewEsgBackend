from fastapi import HTTPException
from typing import Dict, List
from datetime import datetime
from bson import ObjectId
from database import role_access_collection
import uuid

async def update_permissions(company_id: str, plant_id: str, financial_year: str, permissions_data: Dict, user_id: str) -> Dict[str, str]:
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

async def get_accessible_module_ids(
    company_id: str,
    plant_id: str,
    financial_year: str,
    user_role: str
) -> List[str]:
    print(f"get_accessible_module_ids: company_id={company_id}, plant_id={plant_id}, financial_year={financial_year}, user_role={user_role}")
    """
    Fetch module IDs with true permissions for a user role.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2023_2024').
        user_role: Role of the user (e.g., 'admin').

    Returns:
        List of module IDs (UUIDs) with true permissions.

    Raises:
        HTTPException: If document or role is not found.
    """
    
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

    module_ids = [
        key for key, value in role_entry["permissions"].items()
        if value is True and is_valid_uuid(key)
    ]
    
    print(f"Accessible module IDs: {module_ids}")
    return module_ids

def is_valid_uuid(val: str) -> bool:
    """
    Check if a string is a valid UUID.
    """
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False