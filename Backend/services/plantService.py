from typing import Dict, List
import bcrypt
from pydantic import ValidationError
from bson import ObjectId
from datetime import datetime
from models.plantEmployeeModel import Employee, PlantEmployee, PlantManager
from database import company_collection, plants_collection , plants_employees_collection , reports_collection
from fastapi import HTTPException

async def get_section_progress_service(company_id: str, plant_id: str, financial_year: str):
    """
    Fetch section progress for a plant's report from plants_collection.

    Args:
        company_id: Company identifier.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2024-2025').

    Returns:
        Section progress data (e.g., total and answered questions per section).

    Raises:
        HTTPException: If the plant or section_progress is not found.
    """
    
    print(company_id, plant_id, financial_year)
    # Normalize financial year
    normalized_financial_year = financial_year.replace("-", "_")  # e.g., '2024-2025' to '2024_2025'
    print(normalized_financial_year)
    

    # Fetch plant from plants_collection
    plant = await plants_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    if not plant:
        raise HTTPException(
            status_code=404,
            detail=f"Plant {plant_id} for company {company_id} and financial_year {financial_year} not found"
        )

    # Return section_progress
    section_progress = plant.get("section_progress", {})
    return {
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": financial_year,
        "section_progress": section_progress
    }

async def initialize_plant_service(
    company_id: str,
    plant_id: str,
    financial_year: str,
    plant_manager: PlantManager
):
    """
    Initialize a new plant record in plants_employees_collection for a first-time plant manager login.

    Args:
        company_id: Company identifier.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2024-2025').
        plant_name: Name of the plant.
        plant_manager: Plant manager details (name, employee_id, contact_email, contact_phone).

    Returns:
        Initialized plant employee record.

    Raises:
        HTTPException: If the plant already exists or data is invalid.
    """
    normalized_financial_year = financial_year.replace("-", "_")

    # Check if company exists, create if not
    company = await company_collection.find_one({"company_id": company_id})
    if not company:
        await company_collection.insert_one({
            "company_id": company_id,
            "company_name": f"Company {company_id}",  # Placeholder
            "created_at": datetime.utcnow()
        })

    # Check if plant exists in plants_collection, create if not
    plant = await plants_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id
    })
    if not plant:
        await plants_collection.insert_one({
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year,  # Store as provided
            "created_at": datetime.utcnow()
        })

    # Check if plant already exists in plants_employees_collection
    existing_plant = await plants_employees_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    if existing_plant:
        raise HTTPException(
            status_code=400,
            detail=f"Plant {plant_id} for company {company_id} and financial year {financial_year} already initialized"
        )

    # Create new PlantEmployee record
    plant_employee_data = {
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year,
        "plant_manager": plant_manager.dict(),
        "employees": [],
        "created_at": datetime.utcnow(),
        "updated_at": None
    }

    try:
        plant_employee = PlantEmployee(**plant_employee_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid plant data: {str(e)}")

    result = await plants_employees_collection.insert_one(plant_employee.dict(by_alias=True))
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to initialize plant")


async def create_employee_service(company_id: str, plant_id: str, financial_year: str, employee: Employee) -> PlantEmployee:
    """
    Create a new employee for a plant.

    Args:
        company_id: Company identifier.
        plant_id: Plant identifier.
        financial_year: String identifier.
        employee: Employee data (employee_id, name, email, password, department, user_role).
        updated_by: ID of the user creating the employee.

    Returns:
        Updated plant employee record as a PlantEmployee model.

    Raises:
        HTTPException: If the plant or employee data is invalid.
    """
    # Normalize financial year
    normalized_financial_year = financial_year.replace("-", "_")

    # Validate company
    company = await company_collection.find_one({"company_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    # Validate plant
    plant = await plants_employees_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    if not plant:
        raise HTTPException(
            status_code=404,
            detail=f"Plant {plant_id} for company {company_id} and financial year {financial_year} not found"
        )

    # Check for duplicate employee_id or email
    existing_employee = next(
        (e for e in plant.get("employees", []) if e["employee_id"] == employee.employee_id or e["email"] == employee.email),
        None
    )
    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail=f"Employee with ID {employee.employee_id} or email {employee.email} already exists"
        )

    # Hash password
    hashed_password = bcrypt.hashpw(employee.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Prepare employee data
    employee_data = employee.dict()
    employee_data["password"] = hashed_password
    employee_data["updated_at"] = datetime.utcnow()

    # Append new employee
    result = await plants_employees_collection.update_one(
        {
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": normalized_financial_year
        },
        {
            "$push": {"employees": employee_data},
            "$set": {"updated_at": datetime.utcnow()}
        },
        upsert=True
    )

    if result.modified_count == 0 and result.upserted_id is None:
        raise HTTPException(status_code=500, detail="Failed to add employee")

    # Retrieve updated document and convert to PlantEmployee model
    updated_plant = await plants_employees_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    return PlantEmployee(**updated_plant)


async def update_employee_roles_service(
    company_id: str,
    plant_id: str,
    financial_year: str,
    employee_id: str,
    roles: List[str],
    updated_by: str
) -> PlantEmployee:
    """
    Update an employee's user_role list by appending new roles.
    """
    normalized_financial_year = financial_year.replace("-", "_")
    company = await company_collection.find_one({"company_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    plant = await plants_employees_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    if not plant:
        raise HTTPException(
            status_code=404,
            detail=f"Plant {plant_id} for company {company_id} and financial year {financial_year} not found"
        )

    existing_employee = next(
        (e for e in plant.get("employees", []) if e["employee_id"] == employee_id),
        None
    )
    if not existing_employee:
        raise HTTPException(
            status_code=404,
            detail=f"Employee with ID {employee_id} not found"
        )

    existing_roles = existing_employee.get("user_role", [])
    if isinstance(existing_roles, str):
        existing_roles = [existing_roles]

    updated_roles = list(set(existing_roles + roles))

    result = await plants_employees_collection.update_one(
        {
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": normalized_financial_year,
            "employees.employee_id": employee_id
        },
        {
            "$set": {
                "employees.$.user_role": updated_roles,
                "employees.$.updated_by": updated_by,
                "employees.$.updated_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update employee roles")

    updated_plant = await plants_employees_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    for emp in updated_plant.get("employees", []):
        if isinstance(emp.get("user_role"), str):
            emp["user_role"] = [emp["user_role"]]
    updated_plant["_id"] = str(updated_plant["_id"])  # Convert ObjectId to string
    return PlantEmployee(**updated_plant)