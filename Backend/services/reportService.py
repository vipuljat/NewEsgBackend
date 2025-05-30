from fastapi import HTTPException
from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId
from database import company_collection, plants_collection, reports_collection
from models.base import PyObjectId
from models.reportModel import Report, UpdateLog, QuestionUpdate
from report_init import initialize_report
import logging
from services.roleService import get_accessible_questions 
from utils.getCurrentUser import get_current_user

# Mock imports (replace with actual implementations)
from questionsMapping import QUESTION_MAPPINGS

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def normalize_financial_year(financial_year: str) -> str:
    """
    Normalize financial_year by replacing hyphens with underscores (e.g., '2024-2025' to '2024_2025').
    """
    return financial_year.replace("-", "_")

async def create_report(report_data: Report, user_id: str) -> Dict[str, str]:
    """
    Create a new report for a specific plant under a company, initializing all question fields to null.

    Args:
        report_data: Report data including company_id, plant_id, financial_year.
        user_id: ID of the user creating the report.

    Returns:
        Dictionary with success message and report_id.

    Raises:
        HTTPException: If company, plant, or report validation fails.
    """
    # Normalize financial_year
    normalized_financial_year = normalize_financial_year(report_data.financial_year)

    # Validate company existence
    company = await company_collection.find_one({"company_id": report_data.company_id})
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {report_data.company_id} not found")

    # Validate plant existence and association with company
    plant = await plants_collection.find_one({
        "plant_id": report_data.plant_id,
        "company_id": report_data.company_id
    })
    if not plant:
        raise HTTPException(
            status_code=404,
            detail=f"Plant {report_data.plant_id} not found or not associated with company {report_data.company_id}"
        )

    # Check if a report already exists
    if await reports_collection.find_one({
        "company_id": report_data.company_id,
        "plant_id": report_data.plant_id,
        "financial_year": normalized_financial_year
    }):
        raise HTTPException(
            status_code=400,
            detail=f"Report for company {report_data.company_id}, plant {report_data.plant_id}, and financial year {report_data.financial_year} already exists"
        )

    # Initialize report using the modular function
    report_dict = initialize_report(
        company_id=report_data.company_id,
        plant_id=report_data.plant_id,
        financial_year=normalized_financial_year,
        user_id=user_id
    )

    # Validate with Pydantic model
    try:
        report = Report(**report_dict)
    except Exception as e:
        logger.error(f"Failed to validate report with Pydantic: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid report structure: {str(e)}")

    # Explicitly set _id if not set
    if not report.id:
        report.id = PyObjectId()
        logger.debug(f"Generated new _id: {report.id}")

    # Insert report into database
    try:
        report_data_dict = report.dict(by_alias=True, exclude_unset=True)
        logger.debug(f"Inserting report: {report_data_dict}")
        result = await reports_collection.insert_one(report_data_dict)
        logger.debug(f"Insert result: inserted_id={result.inserted_id}")
    except Exception as e:
        logger.error(f"Failed to insert report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create report: {str(e)}")

    # Verify inserted document
    try:
        inserted_report = await reports_collection.find_one({"_id": result.inserted_id})
        if not inserted_report:
            # Rollback: delete the inserted report
            await reports_collection.delete_one({"_id": result.inserted_id})
            logger.error(f"Inserted report not found for _id: {result.inserted_id}")
            raise HTTPException(status_code=500, detail="Report created but not found in database")
    except Exception as e:
        # Rollback: delete the inserted report
        await reports_collection.delete_one({"_id": result.inserted_id})
        logger.error(f"Failed to verify inserted report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to verify report: {str(e)}")

    # Check if inserted_id is valid
    if not result.inserted_id:
        # Rollback: delete the inserted report
        await reports_collection.delete_one({"_id": report.id})
        logger.error(f"inserted_id is None for report: {report_data_dict}")
        raise HTTPException(status_code=500, detail="Failed to retrieve report ID")

    return {
        "message": f"Report for company {report_data.company_id}, plant {report_data.plant_id}, and financial year {report_data.financial_year} created successfully",
        "report_id": str(result.inserted_id)
    }


def cast_value(value: Any, question_id: str) -> Any:
    """
    Cast the value to the expected type based on the question_id and Pydantic model.
    """
    if question_id.startswith("Q18a_"):
        # For Q18a subcomponents (e.g., Q18a_permanent_employees_male)
        try:
            # EmployeeType expects integers
            if value is None:
                return None
            return int(value)  # Convert string to int
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value type for {question_id}: expected integer, got {type(value)}"
            )
    return value  # Default: return as-is for other questions

async def update_report(company_id: str, plant_id: str, financial_year: str, updates: List[QuestionUpdate], user_id: str) -> Dict[str, str]:
    """
    Update specific question responses in an existing report using question IDs.

    Args:
        company_id: Company identifier.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2024-2025').
        updates: List of question updates.
        user_id: ID of the user performing the update.

    Returns:
        Success message.

    Raises:
        HTTPException: If report, plant, or question is invalid, or no access.
    """
    logger.debug(f"Incoming updates: {[update.dict() for update in updates]}")
    normalized_financial_year = normalize_financial_year(financial_year)

    # Validate report existence
    report = await reports_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report for company {company_id}, plant {plant_id}, and financial year {financial_year} not found"
        )
    logger.debug(f"Report before update: {report}")

    # Validate plant existence
    plant = await plants_collection.find_one({
        "plant_id": plant_id,
        "company_id": company_id
    })
    if not plant:
        raise HTTPException(
            status_code=404,
            detail=f"Plant {plant_id} not found or not associated with company {company_id}"
        )

    # Mock user role for access control (replace with actual logic)
    user_role = "hr"  # Replace with actual role retrieval
    accessible_questions = await get_accessible_questions(company_id, plant_id, financial_year, user_role)

    # Prepare update operations
    update_ops = {}
    update_logs = []
    answered_questions_updates = {}

    for update in updates:
        question_id = update.question_id
        new_value = update.value
        if new_value is None:
            logger.warning(f"new_value is None for question_id: {question_id}")

        if question_id not in QUESTION_MAPPINGS:
            raise HTTPException(status_code=400, detail=f"Invalid question_id: {question_id}")
        if question_id not in accessible_questions:
            raise HTTPException(status_code=403, detail=f"No access to question {question_id}")

        mapping = QUESTION_MAPPINGS[question_id]
        
        # Check if it's a composite question
        if "schema_path_composite" in mapping and "subcomponents" in mapping:
            # Handle composite question (e.g., Q18a, Q18b)
            schema_path_base = mapping["schema_path_composite"]
            if not isinstance(new_value, dict):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid value for composite question {question_id}: expected a nested dictionary"
                )

            # Flatten the nested value into granular updates
            for category, genders in new_value.items():
                if not isinstance(genders, dict):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid value format for {question_id}.{category}: expected a dictionary"
                    )
                for gender, value in genders.items():
                    # Construct granular question_id (e.g., Q18a_permanent_employees_male)
                    granular_id = f"{question_id}_{category}_{gender}"
                    if granular_id not in mapping["subcomponents"]:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid subcomponent {granular_id} for composite question {question_id}"
                        )

                    # Get the granular mapping
                    granular_mapping = QUESTION_MAPPINGS.get(granular_id)
                    if not granular_mapping or "schema_path" not in granular_mapping:
                        raise HTTPException(
                            status_code=400,
                            detail=f"No schema_path defined for granular question {granular_id}"
                        )

                    schema_path = granular_mapping["schema_path"]
                    schema_parts = schema_path.split(".")[1:]
                    if not schema_parts:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Invalid schema_path for granular question {granular_id}: {schema_path}"
                        )

                    # Construct report_path (use schema_path directly without appending granular_id)
                    report_path = schema_path

                    # Cast value to correct type
                    casted_value = cast_value(value, granular_id)

                    # Store update operation
                    update_ops[report_path] = casted_value

                    # Get previous value for logging
                    current_value = report
                    for part in report_path.split(".")[:-1]:
                        current_value = current_value.get(part, {})
                    previous_value = current_value.get(gender) if isinstance(current_value, dict) else None

                    # Update answered_questions for null <-> non-null transitions
                    if previous_value is None and casted_value is not None:
                        if schema_parts[0] == "section_a":
                            subsection = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                            answered_questions_updates[f"section_progress.section_a.{subsection}.answered_questions"] = 1
                            answered_questions_updates["section_progress.section_a.total.answered_questions"] = 1
                        elif schema_parts[0] == "section_b":
                            subsection = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                            answered_questions_updates[f"section_progress.section_b.{subsection}.answered_questions"] = 1
                            answered_questions_updates["section_progress.section_b.total.answered_questions"] = 1
                        elif schema_parts[0] == "section_c":
                            principle = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                            answered_questions_updates[f"section_progress.section_c.principles.{principle}.answered_questions"] = 1
                            answered_questions_updates["section_progress.section_c.total.answered_questions"] = 1
                        module = granular_mapping["module"].lower()
                        sub_module = granular_mapping["sub_module"].lower().replace(" ", "_")
                        answered_questions_updates[f"section_progress.modules.{module}.{sub_module}.answered_questions"] = 1
                    elif previous_value is not None and casted_value is None:
                        if schema_parts[0] == "section_a":
                            subsection = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                            answered_questions_updates[f"section_progress.section_a.{subsection}.answered_questions"] = -1
                            answered_questions_updates["section_progress.section_a.total.answered_questions"] = -1
                        elif schema_parts[0] == "section_b":
                            subsection = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                            answered_questions_updates[f"section_progress.section_b.{subsection}.answered_questions"] = -1
                            answered_questions_updates["section_progress.section_b.total.answered_questions"] = -1
                        elif schema_parts[0] == "section_c":
                            principle = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                            answered_questions_updates[f"section_progress.section_c.principles.{principle}.answered_questions"] = -1
                            answered_questions_updates["section_progress.section_c.total.answered_questions"] = -1
                        module = granular_mapping["module"].lower()
                        sub_module = granular_mapping["sub_module"].lower().replace(" ", "_")
                        answered_questions_updates[f"section_progress.modules.][{module}.{sub_module}.answered_questions"] = -1

                    # Log the update
                    update_logs.append(UpdateLog(
                        question_id=granular_id,
                        updated_by=user_id,
                        updated_at=datetime.utcnow(),
                        schema_path=schema_path,
                        previous_value=str(previous_value) if previous_value is not None else None,
                        new_value=str(casted_value) if casted_value is not None else None
                    ).dict())
        else:
            # Handle non-composite (granular) question
            if "schema_path" not in mapping:
                raise HTTPException(
                    status_code=400,
                    detail=f"No schema_path defined for question {question_id}"
                )
            schema_path = mapping["schema_path"]
            schema_parts = schema_path.split(".")[1:]
            if not schema_parts:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid schema_path for question {question_id}: {schema_path}"
                )

            # Construct report_path
            report_path = schema_path

            # Cast value to correct type
            casted_value = cast_value(new_value, question_id)

            # Store update operation
            update_ops[report_path] = casted_value

            # Get previous value for logging
            current_value = report
            for part in report_path.split(".")[:-1]:
                current_value = current_value.get(part, {})
            previous_value = current_value.get(question_id.split(".")[-1]) if isinstance(current_value, dict) else None

            # Update answered_questions for null <-> non-null transitions
            if previous_value is None and casted_value is not None:
                if schema_parts[0] == "section_a":
                    subsection = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                    answered_questions_updates[f"section_progress.section_a.{subsection}.answered_questions"] = 1
                    answered_questions_updates["section_progress.section_a.total.answered_questions"] = 1
                elif schema_parts[0] == "section_b":
                    subsection = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                    answered_questions_updates[f"section_progress.section_b.{subsection}.answered_questions"] = 1
                    answered_questions_updates["section_progress.section_b.total.answered_questions"] = 1
                elif schema_parts[0] == "section_c":
                    principle = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                    answered_questions_updates[f"section_progress.section_c.principles.{principle}.answered_questions"] = 1
                    answered_questions_updates["section_progress.section_c.total.answered_questions"] = 1
                module = mapping["module"].lower()
                sub_module = mapping["sub_module"].lower().replace(" ", "_")
                answered_questions_updates[f"section_progress.modules.{module}.{sub_module}.answered_questions"] = 1
            elif previous_value is not None and casted_value is None:
                if schema_parts[0] == "section_a":
                    subsection = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                    answered_questions_updates[f"section_progress.section_a.{subsection}.answered_questions"] = -1
                    answered_questions_updates["section_progress.section_a.total.answered_questions"] = -1
                elif schema_parts[0] == "section_b":
                    subsection = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                    answered_questions_updates[f"section_progress.section_b.{subsection}.answered_questions"] = -1
                    answered_questions_updates["section_progress.section_b.total.answered_questions"] = -1
                elif schema_parts[0] == "section_c":
                    principle = schema_parts[2] if len(schema_parts) > 2 else schema_parts[-1]
                    answered_questions_updates[f"section_progress.section_c.principles.{principle}.answered_questions"] = -1
                    answered_questions_updates["section_progress.section_c.total.answered_questions"] = -1
                module = mapping["module"].lower()
                sub_module = mapping["sub_module"].lower().replace(" ", "_")
                answered_questions_updates[f"section_progress.modules.{module}.{sub_module}.answered_questions"] = -1

            # Log the update
            update_logs.append(UpdateLog(
                question_id=question_id,
                updated_by=user_id,
                updated_at=datetime.utcnow(),
                schema_path=schema_path,
                previous_value=str(previous_value) if previous_value is not None else None,
                new_value=str(casted_value) if casted_value is not None else None
            ).dict())

    logger.debug(f"Update operations: {update_ops}")
    report_update_dict = {
        "$set": {
            **update_ops,
            "updated_at": datetime.utcnow(),
            "updated_by": user_id
        },
        "$push": {"updates": {"$each": update_logs}}
    }
    logger.debug(f"Report update dict: {report_update_dict}")

    try:
        result = await reports_collection.update_one(
            {
                "company_id": company_id,
                "plant_id": plant_id,
                "financial_year": normalized_financial_year
            },
            report_update_dict
        )
        logger.debug(f"MongoDB update result: modified_count={result.modified_count}, matched_count={result.matched_count}")
        if result.modified_count == 0 and result.matched_count > 0:
            logger.error(f"No changes applied to report. Update ops: {update_ops}, Report: {report}")
            raise HTTPException(status_code=400, detail="No changes applied to the report despite matching document")
        elif result.matched_count == 0:
            logger.error(f"No document matched for update. Query: company_id={company_id}, plant_id={plant_id}, financial_year={normalized_financial_year}")
            raise HTTPException(status_code=404, detail="Report not found during update")
    except Exception as e:
        logger.error(f"Failed to update report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update report: {str(e)}")

    updated_report = await reports_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    logger.debug(f"Report after update: {updated_report}")

    if answered_questions_updates:
        try:
            plant_update_dict = {
                "$inc": answered_questions_updates,
                "$set": {"updated_at": datetime.utcnow()}
            }
            plant_result = await plants_collection.update_one(
                {"plant_id": plant_id, "company_id": company_id},
                plant_update_dict
            )
            if plant_result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update plant answered_questions")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update plant: {str(e)}")

    return {
        "message": f"Report for company {company_id}, plant {plant_id}, and financial year {financial_year} updated successfully"
    }
    
    
    
    

async def get_report(company_id: str, plant_id: str, financial_year: str, user_id: str = "admin_user") -> Dict[str, Any]:
    """
    Fetch a report for a specific company, plant, and financial year, returning only question responses accessible to the user's role.

    Args:
        company_id: Company identifier.
        plant_id: Plant identifier.
        financial_year: Financial year (e.g., '2024-2025').
        user_id: ID of the user requesting the report (default mock).

    Returns:
        Filtered report data as a dictionary, containing only accessible question responses.

    Raises:
        HTTPException: If company, plant, report, or access is invalid.
    """
    logger.debug(f"Fetching report for company_id: {company_id}, plant_id: {plant_id}, financial_year: {financial_year}")

    # Normalize financial_year
    normalized_financial_year = normalize_financial_year(financial_year)

    # Validate company existence
    company = await company_collection.find_one({"company_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    # Validate plant existence and association
    plant = await plants_collection.find_one({
        "plant_id": plant_id,
        "company_id": company_id
    })
    if not plant:
        raise HTTPException(
            status_code=404,
            detail=f"Plant {plant_id} not found or not associated with company {company_id}"
        )

    # Fetch report
    report = await reports_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    })
    if not report:
        raise HTTPException(
            status_code=404,
            detail=f"Report for company {company_id}, plant {plant_id}, and financial_year {financial_year} not found"
        )
    logger.debug(f"Retrieved report keys: {list(report.keys())}")
    
    user_role = "hr"
    # Static accessible questions for hr role (for testing)
    accessible_questions = await get_accessible_questions(company_id, plant_id, financial_year, user_role)
    
    print(accessible_questions)
    
    logger.debug(f"Role {user_role} accessible questions: {accessible_questions}")

    if not accessible_questions:
        raise HTTPException(status_code=403, detail="No access to any questions in this report")

    # Initialize filtered report with metadata
    filtered_report = {
        "company_id": report["company_id"],
        "plant_id": report["plant_id"],
        "financial_year": report["financial_year"],
        "section_a": {},
        "section_b": {},
        "section_c": {},
        "created_at": report.get("created_at"),
        "updated_at": report.get("updated_at"),
        "created_by": report.get("created_by"),
        "updated_by": report.get("updated_by"),
        "_id": str(report["_id"])
    }

    # Copy accessible question responses
    for question_id in accessible_questions:
        if question_id not in QUESTION_MAPPINGS:
            logger.warning(f"Question {question_id} not found in QUESTION_MAPPINGS")
            continue

        schema_path = QUESTION_MAPPINGS[question_id].get("schema_path")
        if not schema_path or not schema_path.startswith(("section_a", "section_b", "section_c")):
            logger.warning(f"Invalid schema_path for question {question_id}: {schema_path}")
            continue

        logger.debug(f"Processing question {question_id} with schema_path: {schema_path}")

        try:
            # Navigate to the question in the original report
            current = report
            path_parts = schema_path.split(".")
            for part in path_parts[:-1]:
                current = current.get(part, {})
                if not isinstance(current, dict):
                    logger.debug(f"Path {part} in {schema_path} is not a dict for {question_id}")
                    break
            value = current.get(path_parts[-1])
            logger.debug(f"Value for {question_id} at {schema_path}: {value}")

            if value is not None:
                # Navigate to the target in the filtered report
                target = filtered_report
                for part in path_parts[:-1]:
                    target = target.setdefault(part, {})
                target[path_parts[-1]] = value
            else:
                logger.debug(f"No data found for {question_id} at {schema_path}")
        except Exception as e:
            logger.error(f"Failed to process question {question_id} with path {schema_path}: {str(e)}")
            continue

    # Validate filtered report with Pydantic
    try:
        Report(**filtered_report)
    except Exception as e:
        logger.error(f"Failed to validate filtered report with Pydantic: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Invalid filtered report structure: {str(e)}")

    logger.debug(f"Filtered report sections: section_a={filtered_report['section_a']}, section_c={filtered_report['section_c']}")
    return filtered_report