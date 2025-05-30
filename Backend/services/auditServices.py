from fastapi import HTTPException
from database import audit_collection
from models.auditModel import AuditLog


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