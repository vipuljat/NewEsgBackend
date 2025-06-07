from typing import Optional
from fastapi import HTTPException
from database import audit_collection
from models.auditModel import ActionLog, AuditLog
from logging import getLogger

logger = getLogger(__name__)

async def get_audit_log_service(company_id: str, plant_id: str, financial_year: str) -> AuditLog:
    """
    Fetch audit log for a company, plant, and financial year.

    Args:
        company_id: ID of the company.
        plant_id: ID of the plant.
        financial_year: Financial year.

    Returns:
        AuditLog object.

    Raises:
        HTTPException: If audit log is not found.
    """
    audit = await audit_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": financial_year
    })
    if not audit:
        raise HTTPException(status_code=404, detail="Audit log not found")
    
    # Convert _id to string and rename to id
    audit["id"] = str(audit["_id"]) if "_id" in audit else None
    audit.pop("_id", None)  # Ensure _id is removed
    
    # Validate and return AuditLog
    try:
        return AuditLog(**audit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate audit log: {str(e)}")
    
    
async def log_action_service(
    company_id: str,
    plant_id: Optional[str],
    financial_year: str,
    action_log: ActionLog
) -> None:
    """
    Append an action to the audit log in MongoDB.

    Args:
        company_id: Company ID.
        plant_id: Plant ID (optional).
        financial_year: Financial year.
        action_log: Action details to log.

    Raises:
        HTTPException: If the database operation fails.
    """
    try:
        query = {
            "company_id": company_id,
            "financial_year": financial_year,
            "plant_id": plant_id if plant_id else None
        }
        update = {
            "$push": {
                "actions": action_log.dict(exclude_unset=True)
            },
            "$setOnInsert": {
                "company_id": company_id,
                "plant_id": plant_id,
                "financial_year": financial_year,
                
            }
        }

        result = await audit_collection.update_one(query, update, upsert=True)
        if result.modified_count == 0 and result.upserted_id is None:
            logger.warning(f"Failed to log action: {action_log.action} for target_id={action_log.target_id}")
            raise HTTPException(status_code=400, detail="No changes applied")

        logger.info(f"Logged action: {action_log.action} for target_id={action_log.target_id}")
    except Exception as e:
        logger.error(f"Error logging action: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")