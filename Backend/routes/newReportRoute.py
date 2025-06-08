from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional
from models.auditModel import ActionLog
from models.newReportModel import Report, CreateReportRequest, QuestionUpdate
from services.auditServices import log_action_service
from services.newReportService import create_report, get_report, update_report, fetch_question_responses
from pydantic import ValidationError, BaseModel
from auth import get_current_user

router = APIRouter()

class QuestionIdsRequest(BaseModel):
    question_ids: List[str]

@router.post("/company/{company_id}/plants/{plant_id}/reportsNew", response_model=Dict[str, str])
async def create_report_endpoint(
    company_id: str,
    plant_id: str,
    report_data: CreateReportRequest,
    user_id: str = Depends(get_current_user)
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

@router.get("/company/{company_id}/plants/{plant_id}/reportsNew/{financial_year}")
async def get_report_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get a report for a specific plant under a company.

    Args:
        company_id: ID of the company from URL.
        plant_id: ID of the plant from URL.
        financial_year: Financial year of the report.
        user_id: ID of the user requesting the report.

    Returns:
        Report data if found.
    """
    try:
        report = await get_report(company_id, plant_id, financial_year)
        if not report:
            # Return empty report structure with proper serialization
            empty_report = {
                "_id": None,  # Include _id field to match structure
                "company_id": company_id,
                "plant_id": plant_id,
                "financial_year": financial_year,
                "responses": {},
                "created_at": None,
                "created_by": None,
                "last_modified_at": None,
                "last_modified_by": None
            }
            return empty_report
        return report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")

@router.patch("/company/{company_id}/plants/{plant_id}/reportsNew/{financial_year}", response_model=Dict[str, str])
async def update_report_endpoint(
    company_id: str,
    plant_id: str,
    financial_year: str,
    updates: List[QuestionUpdate],
    user_id: str = Depends(get_current_user)
):
    """
    Update responses in a report.

    Args:
        company_id: ID of the company from URL.
        plant_id: ID of the plant from URL.
        financial_year: Financial year of the report.
        updates: List of question updates.
        user_id: ID of the user updating the report.

    Returns:
        Dict with success message.
    """
    try:
        result = await update_report(company_id, plant_id, financial_year, updates, user_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update report: {str(e)}")

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
    
    
    
