from typing import Dict
from fastapi import APIRouter, Depends, HTTPException
from models.plantEmployeeModel import Employee, InitializePlantRequest, PlantEmployee, PlantManager, UpdateEmployeeRolesRequest
from services.plantService import get_section_progress_service, initialize_plant_service, create_employee_service, update_employee_roles_service
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

@router.post("/{plant_id}/employees/{financial_year}")
async def create_employee(
    company_id: str,
    plant_id: str,
    financial_year: str,
    employee: Employee
) -> PlantEmployee:
    """
    Create a new employee for a plant.

    Args:
        company_id: Company identifier (query parameter).
        plant_id: Plant identifier (path parameter).
        financial_year: Financial year (path parameter, e.g., '2023-2024').
        employee: Employee data (employee_id, name, email, password, department, user_role).
        current_user: Current user info including user_id, user_role.

    Returns:
        Updated plant employee record as a PlantEmployee model.

    Raises:
        HTTPException: If the plant or employee data is invalid, or user is not admin.
    """

    try:
        return await create_employee_service(company_id, plant_id, financial_year, employee)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    
    
    
@router.put("/{plant_id}/employees/{financial_year}/roles")
async def update_employee_roles(
    company_id: str,
    plant_id: str,
    financial_year: str,
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
            company_id=company_id,
            plant_id=plant_id,
            financial_year=financial_year,
            employee_id=request.employee_id,
            roles=request.roles,
            updated_by=user_id
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")