from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict

from pydantic import BaseModel
from services.roleService import get_accessible_module_ids, get_permissions, update_permissions
from auth import get_current_user, require_company_admin
from models.roleAccessModel import UpdatePermissionsRequest, ModuleAccessRequest

router = APIRouter(
    prefix="/roleAccess",
    tags=["Role Access"],
    responses={404: {"description": "Not found"}}
)


@router.put(
    "/company/{company_id}/plants/{plant_id}/permissions/{financial_year}",
    response_model=Dict[str, str]
)
async def update_permissions_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str,
    request: UpdatePermissionsRequest,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Update role access for an employee in plants_employees collection.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2023-2024').
        request: Request body with employee_name, employee_email, and roles.
        current_user: Current user info including user_id, user_role.

    Returns:
        Dictionary with success message.

    Raises:
        HTTPException: If current user is not admin, user_id missing, employee not found, or update fails.
    """
    if current_user.get("user_role") != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update permissions")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    normalized_financial_year = financial_year.replace("-", "_")
    return await update_permissions(
        company_id=company_id,
        plant_id=plant_id,
        financial_year=normalized_financial_year,
        employee_name=request.employee_name,
        employee_email=request.employee_email,
        roles=request.roles,
        updated_by=user_id
    )


@router.get("/company/{company_id}/plants/{plant_id}/permissions/{financial_year}")
async def get_permissions_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str
):
    return await get_permissions(company_id, plant_id, financial_year)

@router.get(
    "/moduleAccess",
    response_model=Dict[str, List[str]],
    summary="Get accessible module IDs for user roles",
    description="Fetch all module IDs that the user's roles have access to."
)
async def get_module_access_endpoint(
    current_user: Dict = Depends(get_current_user)
):
    """
    Fetch all module IDs that the user's roles have access to.

    Args:
        current_user: Current user info including user_id, user_role (list), company_id, plant_id, financial_year.

    Returns:
        Dictionary with a list of module IDs the roles can access.

    Raises:
        HTTPException: If document or roles are not found.
    """
    print(f"current_user={current_user}")
    
    normalized_financial_year = current_user["financial_year"].replace("-", "_")
    try:
        module_ids = await get_accessible_module_ids(
            company_id=current_user["company_id"],
            plant_id=current_user["plant_id"],
            financial_year=normalized_financial_year,
            user_roles=current_user["user_role"]
        )
        return {"module_ids": module_ids}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

        
        

