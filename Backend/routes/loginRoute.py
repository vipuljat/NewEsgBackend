from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import logging
from typing import Optional, Dict, Any
from bson import ObjectId
from utils.jwt_handler import create_access_token
from database import get_auth_users_collection, get_plants_employees_collection

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter(prefix="/users", tags=["users"])

# Initialize password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Get database collections
auth_users_collection = get_auth_users_collection()
plant_employee_collection = get_plants_employees_collection()

# Request model for login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

# Response model for token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: EmailStr
    user_role: str
    company_id: str
    plant_id: Optional[str] = None  # Optional for company admins

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: LoginRequest):
    """
    Authenticate a user (company admin or plant employee) and return a JWT access token.
    """
    try:
        # Validate database collections
        if auth_users_collection is None:
            logger.error("Database collection 'auth_users' is not initialized")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Database configuration issue"
            )
        if plant_employee_collection is None:
            logger.error("Database collection 'plant_employee' is not initialized")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error: Database configuration issue"
            )

        # Try authenticating as company admin in auth_users
        user: Optional[Dict[str, Any]] = await auth_users_collection.find_one({"email": login_data.email.lower()})
        if user:
            # Validate user _id
            if "_id" not in user:
                logger.error(f"Admin user with email {login_data.email} has missing _id field")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error: User data corrupted"
                )

            # Verify password
            password_hash = user.get("password")
            if not password_hash:
                logger.error(f"Admin user with email {login_data.email} has missing password field")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error: User data corrupted"
                )

            if not pwd_context.verify(login_data.password, password_hash):
                logger.warning(f"Invalid password attempt for admin email: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            # Validate required fields
            required_fields = ["user_role", "company_id"]
            missing_fields = [field for field in required_fields if field not in user or user[field] is None]
            if missing_fields:
                logger.error(f"Missing required fields for admin user_id {user['_id']}: {missing_fields}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"User data incomplete: missing {', '.join(missing_fields)}"
                )

            # Admin user details
            user_id = str(user["_id"])
            user_role = user["user_role"]
            company_id = user["company_id"]
            plant_id = None  # Admins are not plant-specific
            email = user["email"]

            logger.info(f"Admin logged in: user_id={user_id}, user_role={user_role}, company_id={company_id}")

        else:
            # Try authenticating as plant employee in plant_employee
            # Use aggregation to match employee in the employees array
            pipeline = [
                {
                    "$unwind": "$employees"
                },
                {
                    "$match": {
                        "employees.email": login_data.email.lower()
                    }
                },
                {
                    "$project": {
                        "company_id": 1,
                        "plant_id": 1,
                        "employee": "$employees"
                    }
                }
            ]
            employee_result = await plant_employee_collection.aggregate(pipeline).to_list(length=1)
            if not employee_result:
                logger.warning(f"Login attempt with non-existent email: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            employee_data = employee_result[0]
            employee = employee_data["employee"]

            # Verify password
            password_hash = employee.get("password")
            if not password_hash:
                logger.error(f"Employee with email {login_data.email} has missing password field")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error: Employee data corrupted"
                )

            if not pwd_context.verify(login_data.password, password_hash):
                logger.warning(f"Invalid password attempt for employee email: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            # Validate required fields
            required_fields = ["employee_id", "user_role", "email"]
            missing_fields = [field for field in required_fields if field not in employee or employee[field] is None]
            if missing_fields:
                logger.error(f"Missing required fields for employee email {login_data.email}: {missing_fields}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Employee data incomplete: missing {', '.join(missing_fields)}"
                )

            if not employee_data.get("company_id") or not employee_data.get("plant_id"):
                logger.error(f"Missing company_id or plant_id for employee email {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Employee data incomplete: missing company_id or plant_id"
                )

            # Employee details
            user_id = employee["employee_id"]
            user_role = employee["user_role"]
            company_id = employee_data["company_id"]
            plant_id = employee_data["plant_id"]
            email = employee["email"]

            logger.info(f"Employee logged in: user_id={user_id}, user_role={user_role}, company_id={company_id}, plant_id={plant_id}")

        # Generate JWT with user details
        token_data = {
            "sub": email,
            "user_id": user_id,
            "user_role": user_role,
            "company_id": company_id,
            "plant_id": plant_id
        }
        access_token = create_access_token(data=token_data)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            email=email,
            user_role=user_role,
            company_id=company_id,
            plant_id=plant_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login for email {login_data.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )