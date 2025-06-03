from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Any
from pydantic import BaseModel
from routes.loginRoute import router as users_router
from routes.companyRoutes import company_router as company_router
from routes.roleAccessRoutes import router as role_access_router
from routes.plantRoutes import router
from routes.newReportRoute import router as new_report_router
from routes.moduleRoutes import router as module_router
from routes.auditRoutes import router as audit_router
import json
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
active_streams = {}

class MessageRequest(BaseModel):
    message: str
    context: Optional[Dict[Any, Any]] = None

class StreamRequest(BaseModel):
    message: str
    context: Optional[Dict[Any, Any]] = None

def create_prompt_with_context(message: str, context: Optional[Dict[Any, Any]] = None) -> str:
    if not context:
        return message

    # Extract relevant information from context
    question_text = context.get('questionText', '')
    guidance_text = context.get('guidanceText', '')
    metadata = context.get('metadata', {})
    answer = context.get('answer', '')

    # Get requirements from metadata
    requirements = []
    if metadata.get('string_value_required'):
        requirements.append('Text response required')
    if metadata.get('decimal_value_required'):
        requirements.append('Numerical value required')
    if metadata.get('boolean_value_required'):
        requirements.append('Yes/No response required')
    if metadata.get('link_required'):
        requirements.append('Supporting document link required')
    if metadata.get('note_required'):
        requirements.append('Additional notes required')

    requirements_text = '\n'.join([f"- {req}" for req in requirements]) if requirements else "No specific format requirements"

    # Create a structured prompt that includes the context
    structured_prompt = f"""Question Context:
Question: {question_text}
Guidance: {guidance_text}
Current Answer: {answer}
Question Type: {metadata.get('type', 'Not specified')}

Requirements:
{requirements_text}

User Query: {message}

Please provide a response that takes into account the above context, requirements, and specifically addresses the user's query."""

    logger.info(f"Generated prompt with context:\n{structured_prompt}")
    return structured_prompt

@app.post("/api/messages")
async def post_message(request: MessageRequest):
    prompt = create_prompt_with_context(request.message, request.context)
    logger.info(f"Processing message with prompt:\n{prompt}")
    
    if not EXPECTED_API_KEY:
        logger.error("AI service unavailable: API key missing or invalid")
        raise HTTPException(status_code=500, detail="AI service unavailable")

    try:
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
            "user_message": request.message,
            "context": request.context,
            "bot_reply": reply,
            "timestamp": datetime.now(ist).isoformat()
        })
        return {"reply": reply}
    except Exception as e:
        logger.error(f"Error generating text: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/messages/stream")
async def create_stream(request: StreamRequest):
    if not EXPECTED_API_KEY:
        logger.error("AI service unavailable: API key missing or invalid")
        raise HTTPException(status_code=500, detail="AI service unavailable")

    # Create a unique stream ID
    stream_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(len(active_streams))
    
    # Store stream context
    active_streams[stream_id] = {
        "message": request.message,
        "context": request.context
    }
    
    return {"streamId": stream_id}

@app.get("/api/messages/stream/{stream_id}")
async def get_stream(stream_id: str):
    if stream_id not in active_streams:
        raise HTTPException(status_code=404, detail="Stream not found")

    stream_data = active_streams[stream_id]
    prompt = create_prompt_with_context(stream_data["message"], stream_data["context"])
    logger.info(f"Starting stream {stream_id} with prompt:\n{prompt}")

    async def stream_response():
        try:
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )
            stream = client.models.generate_content_stream(
                model=model,
                contents=prompt,
                config=generate_content_config,
            )
            for chunk in stream:
                if chunk.text:
                    logger.info(f"Streaming chunk for {stream_id}: {chunk.text}")
                    yield f"data: {chunk.text}\n\n"
            logger.info(f"Stream {stream_id} complete")
            yield "event: complete\ndata: \n\n"
            
            # Cleanup
            del active_streams[stream_id]
        except Exception as e:
            logger.error(f"Streaming error for {stream_id}: {str(e)}")
            yield f"error: {str(e)}\n\n"
            # Cleanup on error
            del active_streams[stream_id]

    return StreamingResponse(
        stream_response(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

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

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "accept", "Origin", "X-Requested-With"],
)

# Uvicorn for local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)