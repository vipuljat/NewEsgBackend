from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from database import init_db
from routes.loginRoute import router as users_router
from routes.companyRoutes import company_router as company_router
from routes.roleAccessRoutes import router as role_access_router
from routes.plantRoutes import router
from routes.newReportRoute import router as new_report_router
from routes.moduleRoutes import router as module_router
from routes.auditRoutes import router as audit_router
from routes.geminiRoute import router as gemini_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_db()

# Include all routes
app.include_router(users_router)
app.include_router(company_router)
app.include_router(role_access_router)
app.include_router(router)
app.include_router(new_report_router)
app.include_router(module_router)
app.include_router(audit_router)
app.include_router(gemini_router)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "accept", "Origin", "X-Requested-With"],
)

# For local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)