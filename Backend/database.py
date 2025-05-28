from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import settings

# MongoDB connection
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client["esg_database"]

# Single collection for all sections
esg_collection = db["ESGResponses"]

# Existing user collection for general user data
user_collection = db["user"]

# New collection for authentication (email and password)
auth_users_collection = db["authUsers"]

# Collections for your application
company_collection = db["company"]
plants_collection = db["plants"]
role_access_collection = db["role_access_collection"]
roles_collection = db["roles"]
reports_collection = db["reports"]
roles_collection = db["roles"]
plants_employees_collection = db["plants_employees"]

async def init_db():
    """
    Initialize the database with necessary indexes and migrate existing data.
    """
    # Create unique index for reports_collection
    await reports_collection.create_index(
        [("company_id", 1), ("plant_id", 1), ("financial_year", 1)],
        unique=True
    )
    
    # Migrate existing reports to normalize financial_year (e.g., '2024-2025' to '2024_2025')
    async for report in reports_collection.find({"financial_year": {"$regex": "\\d{4}-\\d{4}"}}):
        old_financial_year = report["financial_year"]
        new_financial_year = old_financial_year.replace("-", "_")
        await reports_collection.update_one(
            {"_id": report["_id"]},
            {"$set": {"financial_year": new_financial_year}}
        )
        print(f"Updated report {report['_id']} from {old_financial_year} to {new_financial_year}")

def get_collection():
    return esg_collection

def get_user_collection():
    return user_collection

def get_auth_users_collection():
    return auth_users_collection

def get_company_collection():
    return company_collection


def get_plants_collection():
    return plants_collection    


def get_plants_employees_collection():
    return plants_employees_collection  