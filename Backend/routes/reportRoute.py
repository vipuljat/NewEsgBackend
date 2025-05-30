from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from models.reportModel import Report, QuestionUpdate
from services.reportService import create_report, get_report, update_report
from pydantic import BaseModel, ValidationError

router = APIRouter()

class CreateReportRequest(BaseModel):
    company_id: str
    plant_id: str
    financial_year: str

async def get_current_user_id() -> str:
    # Mock dependency; in production, use OAuth2 or JWT to get user ID
    return "admin_user"

@router.post("/company/{company_id}/plants/{plant_id}/reports", response_model=Dict[str, str])
async def create_report_endpoint(
    company_id: str,
    plant_id: str,
    report_data: CreateReportRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new report for a specific plant under a company using the report_init structure.

    Args:
        company_id: ID of the company from URL.
        plant_id: ID of the plant from URL.
        report_data: Request body with company_id, plant_id, financial_year.
        user_id: ID of the user creating the report.

    Returns:
        Dict with success message and report_id.

    Raises:
        HTTPException: If validation fails or an error occurs.
    """
    try:
        # Validate that report_data matches URL parameters
        if report_data.company_id != company_id:
            raise HTTPException(status_code=400, detail="Report company_id must match URL company_id")
        if report_data.plant_id != plant_id:
            raise HTTPException(status_code=400, detail="Report plant_id must match URL plant_id")

        # Create Report model instance
        report = Report(
            company_id=report_data.company_id,
            plant_id=report_data.plant_id,
            financial_year=report_data.financial_year
        )

        result = await create_report(report, user_id)
        return result
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Invalid report data: {str(e)}")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

@router.patch("/company/{company_id}/plants/{plant_id}/reports/{financial_year}", response_model=Dict[str, str])
async def update_report_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str,
    updates: List[QuestionUpdate],
    user_id: str = Depends(get_current_user_id)
):
    """
    Update specific question responses in an existing report for a specific plant under a company for a financial year.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year of the report (e.g., '2023-2024').
        updates: List of updates with question_id and value.
        user_id: ID of the user performing the update.

    Returns:
        Dict with success message.

    Raises:
        HTTPException: If validation fails or an error occurs.
    """
    try:
        # Normalize financial_year for consistency
        normalized_financial_year = financial_year.replace("_", "-")

        # Call the update_report service function
        result = await update_report(company_id, plant_id, normalized_financial_year, updates, user_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update report: {str(e)}")
    
    
    


@router.get("/company/{company_id}/plants/{plant_id}/reports/{financial_year}")
async def fetch_report(
    company_id: str,
    plant_id: str,
    financial_year: str,
    user_id: str = Depends(get_current_user_id)
):
    return await get_report(company_id, plant_id, financial_year, user_id)