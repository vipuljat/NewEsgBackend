from fastapi import APIRouter, HTTPException
from typing import List
from models.module_model import Module, SubModule, QuestionCategory, Question, ModuleCollection
from services.moduleService import (
    get_all_modules_service,
    get_module_by_id_service,
    create_module_service,
    update_module_service,
    get_submodule_by_id_service,
    create_submodule_service,
    get_question_category_service,
    create_question_category_service,
    get_question_service,
    create_question_service,
    update_question_service
)

router = APIRouter(prefix="/modules", tags=["Modules"])

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
        return await get_module_by_id_service(module_id)
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