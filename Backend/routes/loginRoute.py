from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import logging
from typing import List, Optional, Dict, Any
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
    user_role: List[str]  # Changed to List[str] to handle both plant_manager and employees
    user_name: str
    company_id: str
    plant_id: Optional[str] = None
    financial_year: Optional[str] = None

@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: LoginRequest):
    """
    Authenticate a user (company admin, plant manager, or plant employee) and return a JWT access token.
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
            plant_id = None
            email = user["email"]
            user_name = user.get("name", "Admin User")  # Fallback name if not provided
            financial_year = user.get("financial_year", "2023-2024")  # Fallback if missing

            logger.info(f"Admin logged in: user_id={user_id}, user_role={user_role}, company_id={company_id}")

        else:
            # Try authenticating as plant manager or employee in plant_employee
            pipeline = [
                {
                    "$match": {
                        "$or": [
                            {"plant_manager.contact_email": login_data.email.lower()},
                            {"employees.email": login_data.email.lower()}
                        ]
                    }
                },
                {
                    "$project": {
                        "company_id": 1,
                        "plant_id": 1,
                        "financial_year": 1,
                        "plant_manager": 1,
                        "employees": 1
                    }
                }
            ]
            result = await plant_employee_collection.aggregate(pipeline).to_list(length=1)
            if not result:
                logger.warning(f"Login attempt with non-existent email: {login_data.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )

            data = result[0]
            company_id = data["company_id"]
            plant_id = data["plant_id"]
            financial_year = data.get("financial_year", "2023-2024")

            # Check if the user is the plant manager
            if data.get("plant_manager") and data["plant_manager"].get("contact_email") == login_data.email.lower():
                plant_manager = data["plant_manager"]
                password_hash = plant_manager.get("password")
                if not password_hash:
                    logger.error(f"Plant manager with email {login_data.email} has missing password field")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Internal server error: Plant manager data corrupted"
                    )

                if not pwd_context.verify(login_data.password, password_hash):
                    logger.warning(f"Invalid password attempt for plant manager email: {login_data.email}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )

                # Validate required fields
                required_fields = ["employee_id", "user_role", "contact_email", "name"]
                missing_fields = [field for field in required_fields if field not in plant_manager or plant_manager[field] is None]
                if missing_fields:
                    logger.error(f"Missing required fields for plant manager email {login_data.email}: {missing_fields}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Plant manager data incomplete: missing {', '.join(missing_fields)}"
                    )

                user_id = plant_manager["employee_id"]
                user_role = [plant_manager["user_role"]]  # Convert to list for consistency
                user_name = plant_manager["name"]
                email = plant_manager["contact_email"]

                logger.info(f"Plant manager logged in: user_id={user_id}, user_role={user_role}, company_id={company_id}, plant_id={plant_id}")

            else:
                # Check employees array
                employee = next((emp for emp in data.get("employees", []) if emp["email"] == login_data.email.lower()), None)
                if not employee:
                    logger.warning(f"Login attempt with non-existent employee email: {login_data.email}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid email or password"
                    )

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
                required_fields = ["employee_id", "user_role", "email", "name"]
                missing_fields = [field for field in required_fields if field not in employee or employee[field] is None]
                if missing_fields:
                    logger.error(f"Missing required fields for employee email {login_data.email}: {missing_fields}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Employee data incomplete: missing {', '.join(missing_fields)}"
                    )

                user_id = employee["employee_id"]
                user_role = employee["user_role"]
                user_name = employee["name"]
                email = employee["email"]

                logger.info(f"Employee logged in: user_id={user_id}, user_role={user_role}, company_id={company_id}, plant_id={plant_id}")

        # Generate JWT with user details
        token_data = {
            "sub": email,
            "user_id": user_id,
            "user_role": user_role,
            "user_name": user_name,
            "company_id": company_id,
            "plant_id": plant_id,
            "financial_year": financial_year
        }
        access_token = create_access_token(data=token_data)

        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user_id,
            email=email,
            user_role=user_role,
            user_name=user_name,
            company_id=company_id,
            plant_id=plant_id,
            financial_year=financial_year
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login for email {login_data.email}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )