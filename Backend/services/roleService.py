from fastapi import HTTPException
from typing import Dict, List
from datetime import datetime
from database import role_access_collection, plants_employees_collection, landing_flow_questions_collection
import uuid

async def update_permissions(
    company_id: str,
    plant_id: str,
    financial_year: str,
    employee_name: str,
    employee_email: str,
    roles: List[str],
    updated_by: str
) -> Dict[str, str]:
    """
    Update role access for an employee in plants_employees collection.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2023_2024').
        employee_name: Name of the employee.
        employee_email: Email of the employee.
        roles: List of role IDs to grant access to.
        updated_by: ID of the user updating permissions.

    Returns:
        Dictionary with success message.

    Raises:
        HTTPException: If employee not found or update fails.
    """
    try:
        # Verify employee exists in plants_employees collection
        document = await plants_employees_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year,
            "employees": {
                "$elemMatch": {
                    "name": employee_name,
                    "email": employee_email
                }
            }
        })
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Employee {employee_name} with email {employee_email} not found for company {company_id}, plant {plant_id}, financial year {financial_year}"
            )

        # Find employee in employees array
        employee = next(
            (emp for emp in document["employees"] if emp["name"] == employee_name and emp["email"] == employee_email),
            None
        )
        if not employee:
            raise HTTPException(
                status_code=404,
                detail=f"Employee {employee_name} with email {employee_email} not found"
            )

        # Get existing roles (default to empty list if not set)
        existing_roles = employee.get("roles", [])

        # Combine existing and new roles, removing duplicates
        updated_roles = list(set(existing_roles + roles))

        # Update employee's roles, updated_by, and updated_at
        result = await plants_employees_collection.update_one(
            {
                "company_id": company_id,
                "plant_id": plant_id,
                "financial_year": financial_year,
                "employees": {
                    "$elemMatch": {
                        "name": employee_name,
                        "email": employee_email
                    }
                }
            },
            {
                "$set": {
                    "employees.$.roles": updated_roles,
                    "employees.$.updated_by": updated_by,
                    "employees.$.updated_at": datetime.utcnow()
                }
            }
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="Failed to update employee roles")

        return {"message": "Permissions updated successfully"}
    except HTTPException as e:
        raise e
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
    user_roles: List[str]
) -> List[str]:
    """
    Fetch module IDs with true permissions for a list of user roles.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2023_2024').
        user_roles: List of user roles (e.g., ['admin', 'manager']).

    Returns:
        List of unique module IDs (UUIDs) with true permissions across all roles.

    Raises:
        HTTPException: If document or roles are not found.
    """
    print(f"get_accessible_module_ids: company_id={company_id}, plant_id={plant_id}, financial_year={financial_year}, user_roles={user_roles}")
    
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

    role_permissions = doc.get("role_permissions", [])
    accessible_module_ids = set()

    # Collect module IDs for all roles
    found_roles = []
    for role in user_roles:
        role_entry = next(
            (entry for entry in role_permissions if entry["role"] == role),
            None
        )
        if role_entry:
            found_roles.append(role)
            module_ids = [
                key for key, value in role_entry["permissions"].items()
                if value is True and is_valid_uuid(key)
            ]
            accessible_module_ids.update(module_ids)

    if not found_roles:
        raise HTTPException(
            status_code=404,
            detail=f"None of the roles {user_roles} found in permissions"
        )

    module_ids = list(accessible_module_ids)
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

async def get_accessible_questions(company_id: str, plant_id: str, financial_year: str, user_role: str) -> List[str]:
    """
    Get list of question IDs accessible to a user role.

    Args:
        company_id: Company identifier.
        plant_id: Plant identifier.
        financial_year: Financial year.
        user_role: User role to check permissions for.

    Returns:
        List of question IDs accessible to the user role.
    """
    try:
        # For now, return all questions since we're using the new collection
        questions = await landing_flow_questions_collection.find({}).to_list(None)
        return [q["question_id"] for q in questions]
    except Exception as e:
        print(f"Error getting accessible questions: {str(e)}")
        return []