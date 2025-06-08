from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Dict
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key for JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """
    Get current user from JWT token.
    
    Args:
        token: JWT token from request
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract user info
        user_id: str = payload.get("sub")
        company_id: str = payload.get("company_id")
        plant_id: str = payload.get("plant_id") 
        financial_year: str = payload.get("financial_year")
        
        if user_id is None:
            raise credentials_exception
            
        return {
            "user_id": user_id,
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year
        }
        
    except JWTError:
        raise credentials_exception

async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    Get current user ID from JWT token.
    
    Args:
        token: JWT token from request
        
    Returns:
        User ID string
        
    Raises:
        HTTPException: If token is invalid
    """
    user = await get_current_user(token)
    return user["user_id"] 