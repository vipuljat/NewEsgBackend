from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Dict
from services.roleService import check_module_access, get_permissions, update_permissions

router = APIRouter(
    prefix="/roleAccess",
    tags=["Role Access"],
    responses={404: {"description": "Not found"}}
)

# Placeholder dependency for user authentication
async def get_current_user() -> Dict[str, str]:
    """
    Mock dependency to get the current user_id and user_role.
    Replace with actual OAuth2/JWT dependency in production.
    """
    user = {
        "user_id": "admin123",
        "user_role": "admin"
    }
    if not user.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# Dependency to restrict access to company_admin role
async def require_company_admin(current_user: Dict[str, str] = Depends(get_current_user)) -> Dict[str, str]:
    """
    Ensure the user has the company_admin role.
    """
    if current_user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User role {current_user.get('user_role')} not authorized to manage role access"
        )
    return current_user

@router.put("/company/{company_id}/plants/{plant_id}/permissions/{financial_year}")
async def update_permissions_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str,
    permissions_data: Dict,
    user_id: str = Depends(get_current_user)
):
    return await update_permissions(company_id, plant_id, financial_year, permissions_data, user_id)

@router.get("/company/{company_id}/plants/{plant_id}/permissions/{financial_year}")
async def get_permissions_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str
):
    return await get_permissions(company_id, plant_id, financial_year)

@router.get(
    "/company/{company_id}/plants/{plant_id}/permissions/{financial_year}/module-access",
    response_model=Dict[str, bool],
    summary="Check module access for a user role",
    description="Check if the user's role has access to a specified module."
)
async def check_module_access_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str,
    module_name: str = Query(..., description="Name of the module to check access for"),
    current_user: Dict[str, str] = Depends(require_company_admin)
):
    
    print(f"company_id: {company_id}, plant_id: {plant_id}, financial_year: {financial_year}, module_name: {module_name}, current_user: {current_user}")
    """
    Check if the user's role has access to a specified module.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2023-2024').
        module_name: Name of the module (e.g., 'workforce', 'compliance').
        current_user: Current user info including user_id and user_role.

    Returns:
        Dictionary with 'has_access' indicating if the role can access the module.

    Raises:
        HTTPException: If document, role, or module is invalid.
    """
    
    normalized_financial_year = financial_year.replace("-", "_")
    try:
        has_access = await check_module_access(
            company_id=company_id,
            plant_id=plant_id,
            financial_year=normalized_financial_year,
            user_role=current_user["user_role"],
            module_name=module_name
        )
        return {"has_access": has_access}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )