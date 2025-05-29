from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from typing import Dict
from datetime import datetime, timedelta
from utils.config import settings  # Assumes settings loads SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Adjust to your login endpoint

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Extract user metadata from JWT token.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_role: str = payload.get("user_role")
        company_id: str = payload.get("company_id")
        plant_id: str = payload.get("plant_id")
        financial_year: str = payload.get("financial_year")
        
        if not all([financial_year, user_role, company_id, plant_id]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing required fields",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        print(f"user_role={user_role}, company_id={company_id}, plant_id={plant_id}, financial_year={financial_year}")
        return {
            "user_role": user_role,
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_company_admin(current_user: Dict[str, str] = Depends(get_current_user)) -> Dict[str, str]:
    """
    Ensure the user has the admin role.
    """
    if current_user.get("user_role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User role {current_user.get('user_role')} not authorized to manage role access"
        )
    return current_user