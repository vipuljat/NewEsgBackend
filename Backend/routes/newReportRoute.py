from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from models.newReportModel import Report, CreateReportRequest, QuestionUpdate
from services.newReportService import create_report, get_report, update_report, fetch_question_responses
from pydantic import ValidationError, BaseModel
from auth import get_current_user

router = APIRouter()

class QuestionIdsRequest(BaseModel):
    question_ids: List[str]

async def get_current_user_id() -> str:
    # Mock dependency; in production, use OAuth2 or JWT
    return "admin"

@router.post("/company/{company_id}/plants/{plant_id}/reportsNew", response_model=Dict[str, str])
async def create_report_endpoint(
    company_id: str,
    plant_id: str,
    report_data: CreateReportRequest,
    user_id: str = Depends(get_current_user_id)
):
    """
    Create a new report for a specific plant under a company.

    Args:
        company_id: ID of the company from URL.
        plant_id: ID of the plant from URL.
        report_data: Request body with company_id, plant_id, financial_year.
        user_id: ID of the user creating the report.

    Returns:
        Dict with success message and report_id.
    """
    try:
        # Validate URL parameters
        if report_data.company_id != company_id:
            raise HTTPException(status_code=400, detail="Report company_id must match URL company_id")
        if report_data.plant_id != plant_id:
            raise HTTPException(status_code=400, detail="Report plant_id must match URL plant_id")

        # Create Report instance
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

@router.patch("/company/{company_id}/plants/{plant_id}/reportsNew/{financial_year}", response_model=Dict[str, str])
async def update_report_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str,
    updates: List[QuestionUpdate],
    user_id: str = Depends(get_current_user_id)
):
    """
    Update specific question responses in an existing report.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year (e.g., '2023_2024' or '2023-2024').
        updates: List of updates with question_id, questionname (optional), and response.
        user_id: ID of the user performing the update.

    Returns:
        Dict with success message.
    """
    try:
        # Normalize financial_year
        normalized_financial_year = financial_year.replace("_", "-")

        # Call update_report service
        result = await update_report(company_id, plant_id, normalized_financial_year, updates, user_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update report: {str(e)}")

@router.get("/company/{company_id}/plants/{plant_id}/reportsNew/{financial_year}", response_model=Report)
async def fetch_report(
    company_id: str,
    plant_id: str,
    financial_year: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Fetch a report by company_id, plant_id, and financial_year.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year (e.g., '2023_2024' or '2023-2024').
        user_id: ID of the user.

    Returns:
        Report object with responses.
    """
    try:
        # Normalize financial_year
        normalized_financial_year = financial_year.replace("_", "-")
        report = await get_report(company_id, plant_id, normalized_financial_year, user_id)
        return report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

@router.post("/questionResponses", response_model=Dict[str, Dict])
async def fetch_question_responses_endpoint(
    request: QuestionIdsRequest,
    current_user: Dict[str, str] = Depends(get_current_user)
):
    """
    Fetch responses for specific question IDs from a report, using token metadata.

    Args:
        request: Request body with a list of question IDs.
        current_user: User info from JWT token, including company_id, plant_id, financial_year, user_id.

    Returns:
        Dictionary with question IDs as keys and their responses as values.

    Raises:
        HTTPException: If report or question IDs are invalid.
    """
    try:
        # Normalize financial_year
        normalized_financial_year = current_user["financial_year"].replace("_", "-")

        # Validate question_ids
        if not request.question_ids:
            raise HTTPException(status_code=400, detail="Question IDs list cannot be empty")

        # Fetch responses
        responses = await fetch_question_responses(
            company_id=current_user["company_id"],
            plant_id=current_user["plant_id"],
            financial_year=normalized_financial_year,
            question_ids=request.question_ids,
        )
        return responses
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch question responses: {str(e)}")