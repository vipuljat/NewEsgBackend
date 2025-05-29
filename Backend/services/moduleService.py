from datetime import datetime
from fastapi import HTTPException
from models.module_model import Module, SubModule, QuestionCategory, Question, ModuleCollection
from database import company_collection, plants_collection, get_module_collection
from typing import List, Dict, Optional
import logging

# Initialize a new collection for modules
from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import settings

# Get logger
logger = logging.getLogger(__name__)

# Get database collection
modules_collection = get_module_collection()

async def get_all_modules_service(company_id: str, plant_id: str, financial_year: str) -> List[ModuleCollection]:
    """
    Get all modules for a specific company, plant and financial year.
    """
    # Normalize financial year
    normalized_financial_year = financial_year.replace("-", "_")

    # Validate company and plant exist
    company = await company_collection.find_one({"company_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    plant = await plants_collection.find_one({
        "company_id": company_id,
        "plant_id": plant_id
    })
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant {plant_id} not found")

    # Get modules
    modules = await modules_collection.find({
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": normalized_financial_year
    }).to_list(None)

    if not modules:
        return []

    return modules

async def get_module_by_id(module_id: str) -> Optional[Dict]:
    """
    Get a module by its ID.
    Returns None if module is not found.
    """
    try:
        module = await modules_collection.find_one({"id": module_id})
        return module
    except Exception as e:
        logger.error(f"Error fetching module {module_id}: {str(e)}")
        return None

async def create_module_service(module: Module) -> Module:
    """
    Create a new module.
    """
    # Normalize financial year
    module.financial_year = module.financial_year.replace("-", "_")

    # Validate company and plant exist
    company = await company_collection.find_one({"company_id": module.company_id})
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {module.company_id} not found")

    plant = await plants_collection.find_one({
        "company_id": module.company_id,
        "plant_id": module.plant_id
    })
    if not plant:
        raise HTTPException(status_code=404, detail=f"Plant {module.plant_id} not found")

    # Check if module already exists
    existing_module = await modules_collection.find_one({
        "company_id": module.company_id,
        "plant_id": module.plant_id,
        "financial_year": module.financial_year,
        "module_name": module.module_name
    })
    if existing_module:
        raise HTTPException(
            status_code=400,
            detail=f"Module {module.module_name} already exists for this plant and financial year"
        )

    # Set created_at
    module.created_at = datetime.utcnow()

    # Insert module
    result = await modules_collection.insert_one(module.dict(by_alias=True))
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create module")

    return module

async def update_module_service(module_id: str, module: Module) -> Module:
    """
    Update an existing module.
    """
    existing_module = await modules_collection.find_one({"id": module_id})
    if not existing_module:
        raise HTTPException(status_code=404, detail=f"Module {module_id} not found")

    # Update timestamps
    module.created_at = existing_module["created_at"]
    module.updated_at = datetime.utcnow()

    # Update module
    result = await modules_collection.replace_one(
        {"id": module_id},
        module.dict(by_alias=True)
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update module")

    return module

async def get_submodule_by_id_service(module_id: str, submodule_id: str) -> SubModule:
    """
    Get a specific submodule from a module.
    """
    module = await get_module_by_id_service(module_id)
    submodule = next((s for s in module["submodules"] if s["id"] == submodule_id), None)
    if not submodule:
        raise HTTPException(status_code=404, detail=f"Submodule {submodule_id} not found")
    return SubModule(**submodule)

async def create_submodule_service(module_id: str, submodule: SubModule) -> SubModule:
    """
    Add a new submodule to a module.
    """
    # Get existing module
    module = await get_module_by_id_service(module_id)

    # Check if submodule with same name exists
    if any(s["submodule_name"] == submodule.submodule_name for s in module["submodules"]):
        raise HTTPException(
            status_code=400,
            detail=f"Submodule {submodule.submodule_name} already exists in this module"
        )

    # Add submodule
    result = await modules_collection.update_one(
        {"id": module_id},
        {
            "$push": {"submodules": submodule.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to add submodule")

    return submodule

async def get_question_category_service(
    module_id: str,
    submodule_id: str,
    category_id: str
) -> QuestionCategory:
    """
    Get a specific question category.
    """
    submodule = await get_submodule_by_id_service(module_id, submodule_id)
    category = next(
        (c for c in submodule.question_categories if c.id == category_id),
        None
    )
    if not category:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")
    return category

async def create_question_category_service(
    module_id: str,
    submodule_id: str,
    category: QuestionCategory
) -> QuestionCategory:
    """
    Create a new question category in a submodule.
    """
    # Get existing submodule
    submodule = await get_submodule_by_id_service(module_id, submodule_id)

    # Check if category with same name exists
    if any(c.category_name == category.category_name for c in submodule.question_categories):
        raise HTTPException(
            status_code=400,
            detail=f"Category {category.category_name} already exists in this submodule"
        )

    # Add category
    result = await modules_collection.update_one(
        {
            "id": module_id,
            "submodules.id": submodule_id
        },
        {
            "$push": {"submodules.$.question_categories": category.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to add category")

    return category

async def get_question_service(
    module_id: str,
    submodule_id: str,
    category_id: str,
    question_id: str
) -> Question:
    """
    Get a specific question.
    """
    category = await get_question_category_service(module_id, submodule_id, category_id)
    question = next(
        (q for q in category.questions if q.question_id == question_id),
        None
    )
    if not question:
        raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
    return question

async def create_question_service(
    module_id: str,
    submodule_id: str,
    category_id: str,
    question: Question
) -> Question:
    """
    Create a new question in a category.
    """
    # Get existing category
    category = await get_question_category_service(module_id, submodule_id, category_id)

    # Check if question with same ID exists
    if any(q.question_id == question.question_id for q in category.questions):
        raise HTTPException(
            status_code=400,
            detail=f"Question {question.question_id} already exists in this category"
        )

    # Validate metadata flags against required flags
    if question.string_value_required and not question.has_string_value:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark string value as required when string input is not allowed"
        )
    if question.decimal_value_required and not question.has_decimal_value:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark decimal value as required when decimal input is not allowed"
        )
    if question.boolean_value_required and not question.has_boolean_value:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark boolean value as required when boolean input is not allowed"
        )
    if question.link_required and not question.has_link:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark link as required when link input is not allowed"
        )
    if question.note_required and not question.has_note:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark note as required when note input is not allowed"
        )

    # Add question
    result = await modules_collection.update_one(
        {
            "id": module_id,
            "submodules.id": submodule_id,
            "submodules.question_categories.id": category_id
        },
        {
            "$push": {"submodules.$[sm].question_categories.$[cat].questions": question.dict()},
            "$set": {"updated_at": datetime.utcnow()}
        },
        array_filters=[
            {"sm.id": submodule_id},
            {"cat.id": category_id}
        ]
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to add question")

    return question

async def update_question_service(
    module_id: str,
    submodule_id: str,
    category_id: str,
    question_id: str,
    question: Question
) -> Question:
    """
    Update an existing question.
    """
    # Verify question exists
    existing_question = await get_question_service(
        module_id, submodule_id, category_id, question_id
    )
    if not existing_question:
        raise HTTPException(status_code=404, detail=f"Question {question_id} not found")

    # Validate metadata flags against required flags
    if question.string_value_required and not question.has_string_value:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark string value as required when string input is not allowed"
        )
    if question.decimal_value_required and not question.has_decimal_value:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark decimal value as required when decimal input is not allowed"
        )
    if question.boolean_value_required and not question.has_boolean_value:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark boolean value as required when boolean input is not allowed"
        )
    if question.link_required and not question.has_link:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark link as required when link input is not allowed"
        )
    if question.note_required and not question.has_note:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark note as required when note input is not allowed"
        )

    # Update question
    result = await modules_collection.update_one(
        {
            "id": module_id,
            "submodules.id": submodule_id,
            "submodules.question_categories.id": category_id,
            "submodules.question_categories.questions.question_id": question_id
        },
        {
            "$set": {
                "submodules.$[sm].question_categories.$[cat].questions.$[q]": question.dict(),
                "updated_at": datetime.utcnow()
            }
        },
        array_filters=[
            {"sm.id": submodule_id},
            {"cat.id": category_id},
            {"q.question_id": question_id}
        ]
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update question")

    return question 