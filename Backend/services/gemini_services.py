# To run this code you need to install the following dependencies:
# pip install google-genai

import os
import logging
from typing import Optional, Dict, Any
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        """Initialize the Gemini service with API key."""
        # Load environment variables
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            logger.error("VITE_API_KEY not found in environment variables")
            raise ValueError("VITE_API_KEY not found in environment variables")
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-1.5-flash"

    def create_prompt_with_context(self, message: str, context: Optional[Dict[Any, Any]] = None) -> str:
        """Create a structured prompt with context."""
        if not context:
            return message

        # Extract context information
        question_text = context.get('questionText', '')
        guidance_text = context.get('guidanceText', '')
        metadata = context.get('metadata', {})
        current_answer = context.get('answer', '')

        # Create structured prompt
        structured_prompt = f"""Context:
Question: {question_text}
Guidance: {guidance_text}
Current Answer: {current_answer}
Metadata: {metadata}

User Query: {message}

Please provide a detailed response considering the above context."""

        logger.info(f"Generated prompt with context:\n{structured_prompt}")
        return structured_prompt

    async def generate_content(self, prompt: str) -> str:
        """Generate content using the Gemini model."""
        try:
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )
            
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=generate_content_config,
            )
            
            if not response or not hasattr(response, 'text'):
                return ""
            return str(response.text)
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise

    async def generate_content_stream(self, prompt: str):
        """Generate streaming content using the Gemini model."""
        try:
            generate_content_config = types.GenerateContentConfig(
                response_mime_type="text/plain",
            )
            
            return self.client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=generate_content_config,
            )
        except Exception as e:
            logger.error(f"Error generating content stream: {str(e)}")
            raise

# For testing purposes
if __name__ == "__main__":
    import asyncio
    
    async def test_gemini():
        service = GeminiService()
        test_prompt = """This is my BRSR question and its response. Please improve the response.
        Question: What measures has your organization taken to reduce greenhouse gas emissions?
        Current Answer: Our organization has implemented energy-efficient lighting and reduced travel by 10%."""
        
        response = await service.generate_content(test_prompt)
        print("Generated Response:")
        print(response)

    # Run the test
    asyncio.run(test_gemini())