from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from services.roleService import get_accessible_questions

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
        "user_role": "company_admin"
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
    if current_user.get("user_role") != "company_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User role {current_user.get('user_role')} not authorized to manage role access"
        )
    return current_user

@router.get(
    "/questions",
    response_model=List[str],
    summary="Get questions accessible to a specific role",
    description="Fetch a list of question IDs that a specified role has access to."
)
async def get_role_questions(
    company_id: str,
    plant_id: str,
    financial_year: str,
    user_role: str,
    current_user: Dict[str, str] = Depends(require_company_admin)
) -> List[str]:
    """
    Fetch question IDs accessible to a specific role.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2024-2025').
        role_name: Role to query (e.g., 'hr', 'legal').
        current_user: Current user info including user_id and user_role.

    Returns:
        List of question IDs the role can access.

    Raises:
        HTTPException: If document or role is not found, or for invalid inputs.
    """
    try:
        return await get_accessible_questions(
            company_id=company_id,
            plant_id=plant_id,
            financial_year=financial_year,
            user_role=user_role
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )