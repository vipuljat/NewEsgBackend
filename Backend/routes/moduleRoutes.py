from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict
from models.module_model import Module, SubModule, QuestionCategory, Question, ModuleCollection
from services.moduleService import (
    get_all_modules_service,
    get_module_by_id,
    create_module_service,
    update_module_service,
    get_submodule_by_id_service,
    create_submodule_service,
    get_question_category_service,
    create_question_category_service,
    get_question_service,
    create_question_service,
    update_question_service,
    create_multiple_questions_service
)
from pydantic import BaseModel
from auth import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/modules", tags=["Modules"])

# Pydantic request model for bulk question creation
class MultipleQuestionsRequest(BaseModel):
    questions: List[Question]

# Module endpoints
@router.get("/", response_model=List[ModuleCollection])
async def get_all_modules(company_id: str, plant_id: str, financial_year: str):
    """
    Get all modules for a specific company, plant and financial year.
    """
    try:
        return await get_all_modules_service(company_id, plant_id, financial_year)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{module_id}", response_model=Module)
async def get_module(module_id: str):
    """
    Get a specific module by its ID.
    """
    try:
        return await get_module_by_id(module_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/", response_model=Module)
async def create_module(module: Module):
    """
    Create a new module.
    """
    try:
        return await create_module_service(module)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.patch("/{module_id}", response_model=Module)
async def update_module(module_id: str, module: Module):
    """
    Update an existing module.
    """
    try:
        return await update_module_service(module_id, module)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# SubModule endpoints
@router.get("/{module_id}/submodules/{submodule_id}", response_model=SubModule)
async def get_submodule(module_id: str, submodule_id: str):
    """
    Get a specific submodule from a module.
    """
    try:
        return await get_submodule_by_id_service(module_id, submodule_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{module_id}/submodules", response_model=List[SubModule])
async def get_all_submodules(module_id: str):
    """
    Get all submodules for a specific module.
    """
    try:
        module = await get_module_by_id(module_id)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        
        # Return the submodules list from the module
        return module.get("submodules", [])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{module_id}/submodules", response_model=SubModule)
async def create_submodule(module_id: str, submodule: SubModule):
    """
    Add a new submodule to a module.
    """
    try:
        return await create_submodule_service(module_id, submodule)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Question Category endpoints
@router.get("/{module_id}/submodules/{submodule_id}/categories/{category_id}", response_model=QuestionCategory)
async def get_question_category(module_id: str, submodule_id: str, category_id: str):
    """
    Get a specific question category.
    """
    try:
        return await get_question_category_service(module_id, submodule_id, category_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{module_id}/submodules/{submodule_id}/categories", response_model=QuestionCategory)
async def create_question_category(module_id: str, submodule_id: str, category: QuestionCategory):
    """
    Create a new question category in a submodule.
    """
    try:
        return await create_question_category_service(module_id, submodule_id, category)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Question endpoints
@router.get("/{module_id}/submodules/{submodule_id}/categories/{category_id}/questions/{question_id}", response_model=Question)
async def get_question(module_id: str, submodule_id: str, category_id: str, question_id: str):
    """
    Get a specific question.
    """
    try:
        return await get_question_service(module_id, submodule_id, category_id, question_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{module_id}/submodules/{submodule_id}/categories/{category_id}/questions", response_model=Question)
async def create_question(module_id: str, submodule_id: str, category_id: str, question: Question):
    """
    Create a new question in a category.
    """
    try:
        return await create_question_service(module_id, submodule_id, category_id, question)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.patch("/{module_id}/submodules/{submodule_id}/categories/{category_id}/questions/{question_id}", response_model=Question)
async def update_question(module_id: str, submodule_id: str, category_id: str, question_id: str, question: Question):
    """
    Update an existing question.
    """
    try:
        return await update_question_service(module_id, submodule_id, category_id, question_id, question)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/{module_id}/submodules/{submodule_id}/categories/{category_id}/questions/bulk", response_model=List[Question])
async def create_multiple_questions(
    module_id: str,
    submodule_id: str,
    category_id: str,
    request: MultipleQuestionsRequest
):
    """
    Create multiple questions in a category at once.
    """
    try:
        return await create_multiple_questions_service(
            module_id, submodule_id, category_id, request.questions
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/names")
async def get_module_names(module_ids: List[str], current_user: Dict = Depends(get_current_user)):
    """
    Get module names for a list of module IDs.
    This endpoint is specifically for the sidebar navigation.
    """
    try:
        module_names = []
        for module_id in module_ids:
            module = await get_module_by_id(module_id)
            if module:
                module_names.append({
                    "id": module_id,
                    "name": module.get("module_name", "Unknown Module"),
                    "icon": module.get("icon", "default"),  # Optional: for sidebar icons
                    "route": f"/module/{module_id}"  # Frontend routing path
                })
        
        return {
            "modules": module_names
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching module names: {str(e)}"
        )

@router.post("/details")
async def get_modules_by_ids(module_ids: List[str], current_user: Dict = Depends(get_current_user)):
    """
    Get complete module details for a list of module IDs.
    This endpoint returns full module data for the sidebar and future use.
    """
    try:
        modules_data = []
        for module_id in module_ids:
            module = await get_module_by_id(module_id)
            if module and isinstance(module, dict):
                # Convert ObjectId to string
                if '_id' in module:
                    module['_id'] = str(module['_id'])
                
                # Handle nested ObjectIds in submodules
                if 'submodules' in module:
                    for submodule in module['submodules']:
                        if '_id' in submodule:
                            submodule['_id'] = str(submodule['_id'])
                        # Handle nested categories
                        if 'categories' in submodule:
                            for category in submodule['categories']:
                                if '_id' in category:
                                    category['_id'] = str(category['_id'])
                                # Handle nested questions
                                if 'questions' in category:
                                    for question in category['questions']:
                                        if '_id' in question:
                                            question['_id'] = str(question['_id'])

                # Handle datetime serialization
                if 'created_at' in module:
                    module['created_at'] = module['created_at'].isoformat() if module['created_at'] else None
                if 'updated_at' in module:
                    module['updated_at'] = module['updated_at'].isoformat() if module['updated_at'] else None
                
                modules_data.append(module)
        
        return {
            "modules": modules_data
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching module details: {str(e)}"
        ) 