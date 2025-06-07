from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from models.plantEmployeeModel import Employee, EmployeeUpdate, InitializePlantRequest, PlantEmployee, PlantManager, UpdateEmployeeRolesRequest
from services.plantService import delete_employee_service, get_all_plant_employees_service, get_section_progress_service, initialize_plant_service, create_employee_service, update_employee_roles_service, update_employee_service
from auth import get_current_user

router = APIRouter(prefix="/plants", tags=["Plants"])

@router.get("/{plant_id}/sectionProgress")
async def get_section_progress(company_id: str, plant_id: str, financial_year: str):
    """
    Fetch section progress for a plant's report.

    Args:
        company_id: Company identifier.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2024-2025').

    Returns:
        Section progress data (e.g., total and answered questions per section).

    Raises:
        HTTPException: If the report or plant is not found.
    """
    try:
        return await get_section_progress_service(company_id, plant_id, financial_year)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/initialize")
async def initialize_plant(request: InitializePlantRequest):
    """
    Initialize a new plant record in plants_employees_collection for a first-time plant manager login.

    Args:
        request: Request body containing company_id, plant_id, financial_year, plant_name, and plant_manager.

    Returns:
        Initialized plant employee record.

    Raises:
        HTTPException: If the plant already exists or data is invalid.
    """
    try:
        return await initialize_plant_service(
            request.company_id,
            request.plant_id,
            request.financial_year,
            request.plant_manager
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/employees")
async def create_employee(
    employee: Employee,
    current_user: Dict = Depends(get_current_user)
) -> PlantEmployee:
    """
    Create a new employee for a plant using token data.

    Args:
        employee: Employee data (employee_id, name, email, password, department, user_role).
        current_user: Current user info including company_id, plant_id, financial_year, user_role.

    Returns:
        Updated plant employee record as a PlantEmployee model.

    Raises:
        HTTPException: If the plant or employee data is invalid, or user is not admin.
    """
    if "admin" not in current_user.get("user_role", []):
        raise HTTPException(status_code=403, detail="Only admins can create employees")
    
    try:
        return await create_employee_service(
            company_id=current_user["company_id"],
            plant_id=current_user["plant_id"],
            financial_year=current_user["financial_year"],
            employee=employee
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
@router.put("/employees/updateRole")
async def update_employee_roles(
    request: UpdateEmployeeRolesRequest,
    current_user: Dict = Depends(get_current_user)
) -> PlantEmployee:
    """
    Update an employee's user_role list by appending new roles.

    Args:
        company_id: Company identifier (query parameter).
        plant_id: Plant identifier (path parameter).
        financial_year: Financial year (path parameter, e.g., '2023-2024').
        request: Request body with employee_id and roles to append.
        current_user: Current user info including user_id, user_role.

    Returns:
        Updated plant employee record as a PlantEmployee model.

    Raises:
        HTTPException: If the plant, employee, or user is invalid.
    """
    if "admin" not in current_user.get("user_role", []):
        raise HTTPException(status_code=403, detail="Only admins can update employee roles")

    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    try:
        return await update_employee_roles_service(
            company_id=current_user["company_id"],
            plant_id=current_user["plant_id"],
            financial_year=current_user["financial_year"].replace("-", "_"),
            employee_id=request.employee_id,
            roles=request.roles,
            updated_by=user_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
    
@router.patch("/employees")
async def update_employee(
    employee_update: EmployeeUpdate,
    current_user: Dict = Depends(get_current_user)
) -> PlantEmployee:
    if "admin" not in current_user.get("user_role", []) and "admin" not in current_user.get("user_role", []):
        raise HTTPException(status_code=403, detail="Only admins can update employees")
    try:
        return await update_employee_service(
            company_id=current_user["company_id"],
            plant_id=current_user["plant_id"],
            financial_year=current_user["financial_year"],
            employee_update=employee_update
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/employees")
async def get_all_plant_employees(
    current_user: Dict = Depends(get_current_user)
):
    """
    Fetch all employees for the authenticated user's plant, accessible only to admin.

    Args:
        current_user: Current user info including user_id, user_role, company_id, plant_id, financial_year.

    Returns:
        List of employees for the user's plant.

    Raises:
        HTTPException: If the user is not a admin, or if the plant or data is invalid.
    """
    if "admin" not in current_user.get("user_role", []):
        raise HTTPException(status_code=403, detail="No access allowed: Only admins can view employees")

    try:
        employees = await get_all_plant_employees_service(
            company_id=current_user["company_id"],
            plant_id=current_user["plant_id"],
            financial_year=current_user["financial_year"].replace("-", "_")
        )
        return employees
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
class EmployeeDeleteRequest(BaseModel):
    employee_id: str

@router.delete("/employees/delete")
async def delete_employee(
    request: EmployeeDeleteRequest,
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    
   
    """
    Delete an employee by ID, accessible only to admin.

    Args:
        request: Request body containing employee_id.
        current_user: Current user info including user_id, user_role, company_id, plant_id, financial_year.

    Returns:
        Confirmation message.

    Raises:
        HTTPException: If the user is not an admin, or if the plant or data is invalid.
    """
    if "admin" not in current_user.get("user_role", []):
        raise HTTPException(status_code=403, detail="No access allowed: Only admins can delete employees")

    print(f"Deleting employee with ID:", request.employee_id)
    
    try:
        result = await delete_employee_service(
            company_id=current_user["company_id"],
            plant_id=current_user["plant_id"],
            financial_year=current_user["financial_year"].replace("-", "_"),
            employee_id=request.employee_id
        )
        return {"detail": "Employee deleted successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")