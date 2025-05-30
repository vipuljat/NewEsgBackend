from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from routes.plantRoutes import router as plant_router
from routes.loginRoute import router as users_router
from routes.companyRoutes import company_router as company_router
from routes.roleAccessRoutes import router as role_access_router
from routes.plantRoutes import router
from routes.newReportRoute import router as new_report_router
from routes.moduleRoutes import router as module_router
from routes.auditRoutes import router as audit_router
import logging
from database import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()
    
# Include the question routes#
#app.include_router(plant_router)

# Include the users routes (for login)
app.include_router(users_router)

# Include the company routes
app.include_router(company_router)


# Include the role access routes
app.include_router(role_access_router)

# Include the plant routes
app.include_router(router)

# Include the new report routes
app.include_router(new_report_router)

# Include the module routes
app.include_router(module_router)

# Include the audit routes
app.include_router(audit_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS","PATCH"],
    allow_headers=["Content-Type", "Authorization", "accept", "Origin", "X-Requested-With"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)