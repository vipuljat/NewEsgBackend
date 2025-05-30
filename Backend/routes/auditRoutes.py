from fastapi import APIRouter, HTTPException
from models.auditModel import AuditLog
from services.auditServices import get_audit_log_service  # You will implement this

router = APIRouter(prefix="/audit", tags=["Audit"])

@router.get("/{company_id}/{plant_id}/{financial_year}", response_model=AuditLog)
async def get_audit_log(company_id: str, plant_id: str, financial_year: str):
    """
    Fetch audit log for a company, plant, and financial year.
    """
    try:
        return await get_audit_log_service(company_id, plant_id, financial_year)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch audit log: {str(e)}")