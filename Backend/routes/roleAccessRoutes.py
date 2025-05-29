from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from services.roleService import get_accessible_module_ids, get_permissions, update_permissions
from auth import get_current_user, require_company_admin

router = APIRouter(
    prefix="/roleAccess",
    tags=["Role Access"],
    responses={404: {"description": "Not found"}}
)

@router.put("/company/{company_id}/plants/{plant_id}/permissions/{financial_year}")
async def update_permissions_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str,
    permissions_data: Dict,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    return await update_permissions(company_id, plant_id, financial_year, permissions_data, current_user["user_id"])

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
    summary="Get accessible module IDs for a user role",
    description="Fetch all module IDs that the user's role has access to."
)
async def get_module_access_endpoint(
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Fetch all module IDs that the user's role has access to.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2023-2024').
        current_user: Current user info including user_id, user_role, company_id, plant_id.

    Returns:
        Dictionary with a list of module IDs the role can access.

    Raises:
        HTTPException: If document or role is not found.
    """
    print(f"current_user={current_user}")
    
    normalized_financial_year = current_user["financial_year"].replace("-", "_")
    try:
        
        module_ids = await get_accessible_module_ids(
            company_id=current_user["company_id"],
            plant_id=current_user["plant_id"],
            financial_year=normalized_financial_year,
            user_role=current_user["user_role"]
        )
        return {"module_ids": module_ids}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )