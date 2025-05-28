from fastapi import APIRouter, HTTPException
from models.plantEmployeeModel import Employee, InitializePlantRequest, PlantManager
from services.plantService import get_section_progress_service, initialize_plant_service, create_employee_service

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

@router.post("/{plant_id}/employees")
async def create_employee(company_id: str, plant_id: str, financial_year: str, employee: Employee):
    """
    Create a new employee for a plant.

    Args:
        company_id: Company identifier.
        plant_id: Plant identifier.
        financial_year: String identifier.
        employee: Employee data (employee_id, name, email, department, user_role).

    Returns:
        Updated plant employee record.

    Raises:
        HTTPException: If the plant or employee data is invalid.
    """
    try:
        return await create_employee_service(company_id, plant_id, financial_year, employee)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")