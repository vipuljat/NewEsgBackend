from fastapi import HTTPException
from typing import Dict, List, Optional
from models.newReportModel import Report, QuestionUpdate
from models.tableQuestionResponse import TableQuestionResponse
from datetime import datetime
import json
from database import new_reports_collection, audit_collection
import pytz
from bson import ObjectId

def normalize_financial_year(financial_year: str) -> str:
    """Normalize financial year format by replacing underscores with hyphens."""
    return financial_year.replace("_", "-")

def serialize_mongodb_doc(doc: Dict) -> Dict:
    """Serialize MongoDB document by converting ObjectId to string."""
    if not doc:
        return None
    
    # Convert ObjectId to string
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    
    return doc

async def create_report(report: Report, user_id: str) -> Dict[str, str]:
    """
    Create a new report in the database.

    Args:
        report: Report model instance.
        user_id: ID of the user creating the report.

    Returns:
        Dict with success message and report_id.

    Raises:
        HTTPException: If creation fails.
    """
    try:
        # Normalize financial year
        normalized_financial_year = normalize_financial_year(report.financial_year)
        
        # Check if report already exists
        existing = await new_reports_collection.find_one({
            "company_id": report.company_id,
            "plant_id": report.plant_id,
            "financial_year": normalized_financial_year
        })
        
        if existing:
            raise HTTPException(status_code=400, detail="Report already exists")
            
        # Initialize report with empty responses
        report_dict = {
            "company_id": report.company_id,
            "plant_id": report.plant_id,
            "financial_year": normalized_financial_year,
            "responses": {},
            "created_at": datetime.now(pytz.UTC),
            "created_by": user_id,
            "last_modified_at": datetime.now(pytz.UTC),
            "last_modified_by": user_id
        }
        
        result = await new_reports_collection.insert_one(report_dict)
        return {"message": "Report created successfully", "report_id": str(result.inserted_id)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

async def get_report(company_id: str, plant_id: str, financial_year: str) -> Optional[Dict]:
    """
    Get a report from the database.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year (e.g., '2023-2024' or '2023_2024').

    Returns:
        Report dict if found, None otherwise.

    Raises:
        HTTPException: If retrieval fails.
    """
    try:
        # Normalize financial year
        normalized_financial_year = normalize_financial_year(financial_year)
        
        report = await new_reports_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": normalized_financial_year
        })

        # Serialize MongoDB document
        return serialize_mongodb_doc(report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get report: {str(e)}")

# Helper: Determine if a question is table-type (stub, replace with real logic)
def is_table_question(question_id: str) -> bool:
    # TODO: Replace with actual metadata/mapping lookup
    return question_id.startswith("TBL_")  # Example: all table questions start with 'TBL_'

async def update_report(
    company_id: str,
    plant_id: str,
    financial_year: str,
    updates: List[QuestionUpdate],
    user_id: str
) -> Dict[str, str]:
    """
    Update question responses in a report.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year (e.g., '2023-2024' or '2023_2024').
        updates: List of updates with question_id, response (string_value, bool_value, decimal_value, link, note).
        user_id: ID of the user performing the update.

    Returns:
        Dict with success message.

    Raises:
        HTTPException: If update fails.
    """
    try:
        # Normalize financial year
        normalized_financial_year = normalize_financial_year(financial_year)
        
        # Get existing report
        report = await new_reports_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": normalized_financial_year
        })
        
        if not report:
            # Create new report if it doesn't exist
            report = {
                "company_id": company_id,
                "plant_id": plant_id,
                "financial_year": normalized_financial_year,
                "responses": {},
                "created_at": datetime.now(pytz.UTC),
                "created_by": user_id,
                "last_modified_at": datetime.now(pytz.UTC),
                "last_modified_by": user_id
            }
            await new_reports_collection.insert_one(report)
        
        # Update responses
        responses = report.get("responses", {})
        for update in updates:
            responses[update.question_id] = update.response
            
        # Update the report
        await new_reports_collection.update_one(
            {
                "company_id": company_id,
                "plant_id": plant_id,
                "financial_year": normalized_financial_year
            },
            {
                "$set": {
                    "responses": responses,
                    "last_modified_at": datetime.now(pytz.UTC),
                    "last_modified_by": user_id
                }
            }
        )
        
        return {"message": "Report updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update report: {str(e)}")

async def fetch_question_responses(
    company_id: str,
    plant_id: str,
    financial_year: str,
    question_ids: List[str],
) -> Dict[str, Dict]:
    """
    Fetch responses for specific question IDs from a report.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year.
        question_ids: List of question IDs to fetch.
        user_id: ID of the user.

    Returns:
        Dictionary with question IDs as keys and their responses as values.

    Raises:
        HTTPException: If report or question IDs are invalid.
    """
    try:
        # Fetch report
        report = await new_reports_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year
        })
        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"No report found for company {company_id}, plant {plant_id}, financial year {financial_year}"
            )

        # Extract responses
        responses = report.get("responses", {})
        result = {}
        invalid_ids = []

        for qid in question_ids:
            if qid in responses:
                # Use correct model for table-type questions
                if is_table_question(qid):
                    try:
                        result[qid] = TableQuestionResponse(**responses[qid]).dict()
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f"Corrupt table response for {qid}: {str(e)}")
                else:
                    result[qid] = responses[qid]
            else:
                invalid_ids.append(qid)

        if invalid_ids:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid question IDs: {', '.join(invalid_ids)}"
            )

        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch question responses: {str(e)}")