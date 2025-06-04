from fastapi import HTTPException
from typing import Dict, List, Optional
from models.newReportModel import Report, QuestionUpdate
from models.tableQuestionResponse import TableQuestionResponse
from datetime import datetime
import json
from database import new_reports_collection, audit_collection

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
        report_dict = report.dict(by_alias=True, exclude_unset=True)
        report_dict["created_by"] = user_id
        report_dict["created_at"] = datetime.utcnow()
        report_dict["updated_at"] = report_dict["created_at"]
        report_dict["responses"] = {}  # Initialize empty responses
        report_dict["updates"] = []

        result = await new_reports_collection.insert_one(report_dict)
        return {"message": "Report created successfully", "report_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

async def get_report(company_id: str, plant_id: str, financial_year: str, user_id: str) -> Report:
    """
    Fetch a report by company_id, plant_id, and financial_year.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year (e.g., '2023-2024').
        user_id: ID of the user (for potential access control).

    Returns:
        Report object.

    Raises:
        HTTPException: If report not found or fetch fails.
    """
    try:
        report = await new_reports_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year
        })
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return Report(**report)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch report: {str(e)}")

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
        financial_year: Financial year (e.g., '2023-2024').
        updates: List of updates with question_id, response (string_value, bool_value, decimal_value, link, note).
        user_id: ID of the user performing the update.

    Returns:
        Dict with success message.

    Raises:
        HTTPException: If update fails.
    """
    try:
        # Find the report
        report = await new_reports_collection.find_one({
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year
        })
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        # Prepare update operations
        update_ops = {}
        update_logs = []
        current_time = datetime.utcnow()

        for update in updates:
            question_id = update.question_id
            new_response = {}
            if update.response is not None:
                # Use correct model for table-type questions
                if is_table_question(question_id):
                    if not isinstance(update.response, TableQuestionResponse):
                        # Try to coerce dict to TableQuestionResponse
                        try:
                            new_response = TableQuestionResponse(**update.response).dict(exclude_unset=True)
                        except Exception as e:
                            raise HTTPException(status_code=400, detail=f"Invalid table response for {question_id}: {str(e)}")
                    else:
                        new_response = update.response.dict(exclude_unset=True)
                else:
                    new_response.update(update.response.dict(exclude_unset=True))

            # If no fields provided, skip update
            if not new_response:
                continue

            # Initialize or update response
            if question_id not in report.get("responses", {}):
                # Initialize with defaults if new
                update_ops[f"responses.{question_id}"] = new_response
            else:
                # Update existing fields
                for key, value in new_response.items():
                    update_ops[f"responses.{question_id}.{key}"] = value

            # Log the update
            previous_value = report.get("responses", {}).get(question_id, {})
            new_value = new_response
            update_logs.append({
                "question_id": question_id,
                "updated_by": user_id,
                "updated_at": current_time,
                "previous_value": json.dumps(previous_value) if previous_value else None,
                "new_value": json.dumps(new_value)
            })

        # Apply updates
        if update_ops:
            update_ops["updated_at"] = current_time
            result = await new_reports_collection.update_one(
                {"company_id": company_id, "plant_id": plant_id, "financial_year": financial_year},
                {"$set": update_ops, "$push": {"updates": {"$each": update_logs}}}
            )
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update report")

            # Also update the audit collection
            await audit_collection.update_one(
                {"company_id": company_id, "plant_id": plant_id, "financial_year": financial_year},
                {"$push": {"updates": {"$each": update_logs}}},
                upsert=True
            )

        return {"message": "Report updated successfully"}
    except HTTPException as e:
        raise e
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