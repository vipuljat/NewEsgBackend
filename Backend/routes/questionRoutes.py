from fastapi import APIRouter, HTTPException
from typing import List
from models.module_model import Question
from database import landing_flow_questions_collection

router = APIRouter()

@router.get("/questions/module/{module_id}", response_model=List[Question])
async def get_questions_by_module(module_id: str):
    """
    Get all questions for a specific module.
    
    Args:
        module_id: ID of the module to fetch questions for.
        
    Returns:
        List of questions.
    """
    try:
        # Fetch all questions for the module
        questions = await landing_flow_questions_collection.find({}).to_list(None)
        if not questions:
            return []
            
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch questions: {str(e)}") 