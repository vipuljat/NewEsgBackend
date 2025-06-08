from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from routes.loginRoute import router as users_router
from routes.companyRoutes import company_router as company_router
from routes.roleAccessRoutes import router as role_access_router
from routes.plantRoutes import router
from routes.newReportRoute import router as new_report_router
from routes.moduleRoutes import router as module_router
from routes.auditRoutes import router as audit_router
from routes.geminiRoute import router as gemini_router
from routes import (
    companyRoutes,
    plantRoutes,
    reportRoute,
    newReportRoute,
    roleAccessRoutes,
    moduleRoutes,
    questionRoutes
)
import logging
from database import init_db
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from datetime import datetime
import pytz

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
EXPECTED_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini client
if not EXPECTED_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

client = genai.Client(api_key=EXPECTED_API_KEY)
model = "gemini-1.5-flash"

app = FastAPI()

# Mock message storage (replace with a database in production)
messages = []

class MessageRequest(BaseModel):
    message: str

@app.get("/api/messages")
async def get_messages():
    return messages

@app.post("/api/messages")
async def post_message(request: MessageRequest):
    prompt = request.message
    
    if not EXPECTED_API_KEY:
        logger.error("AI service unavailable: API key missing or invalid")
        raise HTTPException(status_code=500, detail="AI service unavailable")

    try:
        # Use generate_content (synchronous) for non-streaming response
        generate_content_config = types.GenerateContentConfig(
            response_mime_type="text/plain",
        )
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config=generate_content_config,
        )
        reply = response.text
        message_id = len(messages) + 1
        ist = pytz.timezone('Asia/Kolkata')
        messages.append({
            "message_id": message_id,
            "user_message": prompt,
            "bot_reply": reply,
            "timestamp": datetime.now(ist).isoformat()  # Store timestamp in IST
        })
        return {"reply": reply}
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/messages/stream")
async def stream_message(request: Request, message: str):
    if not EXPECTED_API_KEY:
        logger.error("AI service unavailable: API key missing or invalid")
        raise HTTPException(status_code=500, detail="AI service unavailable")

    async def stream_response():
        try:
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )
            # Use generate_content_stream for streaming response
            stream = client.models.generate_content_stream(
                model=model,
                contents=message,
                config=generate_content_config,
            )
            for chunk in stream:
                if chunk.text:
                    logger.info(f"Streaming chunk: {chunk.text}")
                    yield f"data: {chunk.text}\n\n"
            logger.info("Streaming complete")
            yield "event: complete\ndata: \n\n"
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            yield f"error: {str(e)}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})

@app.on_event("startup")
async def startup_event():
    await init_db()

# Include the routes
app.include_router(users_router)
app.include_router(company_router)
app.include_router(role_access_router)
app.include_router(router)
app.include_router(new_report_router)
app.include_router(module_router)
app.include_router(audit_router)
app.include_router(gemini_router)
app.include_router(companyRoutes.company_router)
app.include_router(plantRoutes.router)
app.include_router(reportRoute.router)
app.include_router(newReportRoute.router)
app.include_router(roleAccessRoutes.router)
app.include_router(moduleRoutes.router)
app.include_router(questionRoutes.router)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Content-Type", 
        "Authorization", 
        "accept", 
        "Origin", 
        "X-Requested-With",
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers"
    ],
    expose_headers=[
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Credentials",
        "Access-Control-Allow-Methods",
        "Access-Control-Allow-Headers"
    ]
)

# Uvicorn for local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# Note: This code is designed to run with FastAPI and Uvicorn.