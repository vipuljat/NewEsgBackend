from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from typing import Any, Dict, Optional
from database import company_collection, plants_collection
from models.companyModel import Company
from models.plantModel import Plant, Progress, SectionProgress, SectionCProgress, PrincipleProgress, SectionAProgress, SectionBProgress, ModulesProgress, HRModule, LegalModule, FinanceModule, AdminModule, EnvironmentModule, ModuleSubSectionProgress

async def create_plant(company_id: str, plant_data: Dict[str, Any], user_role: str) -> Dict[str, str]:
    """
    Create a new plant for a specific company with required fields, initializing progress with hardcoded total_questions.
    """
    # Check if company exists
    company: Optional[Dict[str, Any]] = await company_collection.find_one({"company_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail=f"Company {company_id} not found")

    # Get the company's ObjectId
    company_object_id = company["_id"]
    
    # Validate company as Pydantic model
    try:
        company_model = Company(**company)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid company data: {str(e)}")

    # Check user role authorization
    allowed_roles = ["company_admin"]
    if user_role not in allowed_roles:
        raise HTTPException(
            status_code=403,
            detail=f"User role {user_role} not authorized to create plants for {company_id}"
        )

    # Check if plant_id is unique
    plant_id = plant_data.get("plant_id")
    if not plant_id:
        raise HTTPException(status_code=400, detail="plant_id is required")
    if await plants_collection.find_one({"plant_id": plant_id}):
        raise HTTPException(status_code=400, detail=f"Plant {plant_id} already exists")

    # Initialize section_progress with hardcoded total_questions
    default_section_progress = SectionProgress(
        total_questions=0,
        answered_questions=0
    )
    module_subsection_progress = ModuleSubSectionProgress(
        total_questions=0,
        answered_questions=0
    )

    # Hardcoded question counts
    section_a_progress = SectionAProgress(
        entity_details=ModuleSubSectionProgress(total_questions=13, answered_questions=0),
        stock_and_subsidiaries=ModuleSubSectionProgress(total_questions=1, answered_questions=0),
        products_and_operations=ModuleSubSectionProgress(total_questions=6, answered_questions=0),
        csr_and_governance=ModuleSubSectionProgress(total_questions=5, answered_questions=0),
        employees=ModuleSubSectionProgress(total_questions=4, answered_questions=0),
        total=SectionProgress(total_questions=29, answered_questions=0)
    )

    section_b_progress = SectionBProgress(
        policy_and_governance=ModuleSubSectionProgress(total_questions=12, answered_questions=0),
        others=ModuleSubSectionProgress(total_questions=0, answered_questions=0),
        total=SectionProgress(total_questions=12, answered_questions=0)
    )

    principle_progress = PrincipleProgress(
        principle_1=SectionProgress(total_questions=7, answered_questions=0),
        principle_2=SectionProgress(total_questions=5, answered_questions=0),
        principle_3=SectionProgress(total_questions=15, answered_questions=0),
        principle_4=SectionProgress(total_questions=2, answered_questions=0),
        principle_5=SectionProgress(total_questions=10, answered_questions=0),
        principle_6=SectionProgress(total_questions=12, answered_questions=0),
        principle_7=SectionProgress(total_questions=3, answered_questions=0),
        principle_8=SectionProgress(total_questions=4, answered_questions=0),
        principle_9=SectionProgress(total_questions=6, answered_questions=0)
    )

    section_c_progress = SectionCProgress(
        total=SectionProgress(total_questions=64, answered_questions=0),
        principles=principle_progress
    )

    modules_progress = ModulesProgress(
        workforce=HRModule(
            workforce_details=ModuleSubSectionProgress(total_questions=4, answered_questions=0),
            employee_wellbeing=ModuleSubSectionProgress(total_questions=15, answered_questions=0),
            human_rights=ModuleSubSectionProgress(total_questions=10, answered_questions=0),
            retirement=ModuleSubSectionProgress(total_questions=0, answered_questions=0),
            others=ModuleSubSectionProgress(total_questions=0, answered_questions=0)
        ),
        legal=LegalModule(
            policy_and_governance=ModuleSubSectionProgress(total_questions=12, answered_questions=0),
            ethical_conduct=ModuleSubSectionProgress(total_questions=7, answered_questions=0),
            policy_advocacy=ModuleSubSectionProgress(total_questions=3, answered_questions=0),
            others=ModuleSubSectionProgress(total_questions=0, answered_questions=0)
        ),
        finance=FinanceModule(
            products_and_services=ModuleSubSectionProgress(total_questions=2, answered_questions=0),
            csr=ModuleSubSectionProgress(total_questions=3, answered_questions=0),
            inclusive_growth=ModuleSubSectionProgress(total_questions=4, answered_questions=0),
            transparency_and_governance=ModuleSubSectionProgress(total_questions=2, answered_questions=0),
            consumer_responsibility=ModuleSubSectionProgress(total_questions=6, answered_questions=0)
        ),
        admin=AdminModule(
            entity_details=ModuleSubSectionProgress(total_questions=13, answered_questions=0),
            operations=ModuleSubSectionProgress(total_questions=4, answered_questions=0),
            corporate_structure=ModuleSubSectionProgress(total_questions=1, answered_questions=0),
            stakeholder_engagement=ModuleSubSectionProgress(total_questions=2, answered_questions=0)
        ),
        environment=EnvironmentModule(
            sustainable_products=ModuleSubSectionProgress(total_questions=5, answered_questions=0),
            energy_emission=ModuleSubSectionProgress(total_questions=5, answered_questions=0),
            water_and_waste=ModuleSubSectionProgress(total_questions=3, answered_questions=0),
            environmental_compliance=ModuleSubSectionProgress(total_questions=4, answered_questions=0)
        )
    )

    progress = Progress(
        section_a=section_a_progress,
        section_b=section_b_progress,
        section_c=section_c_progress,
        modules=modules_progress
    )

    # Prepare plant data
    plant_data.update({
        "company_id": company_id,  # Store as string per Plant model
        "section_progress": progress.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })

    # Validate plant data with Pydantic model
    try:
        plant_model = Plant(**plant_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid plant data: {str(e)}")

    # Insert plant into the database
    try:
        result = await plants_collection.insert_one(plant_model.dict(by_alias=True, exclude_unset=True))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plant: {str(e)}")

    # Update company's plants array
    try:
        update_result = await company_collection.update_one(
            {"_id": company_object_id},
            {"$push": {"plants": plant_id}}
        )
        if update_result.modified_count == 0:
            await plants_collection.delete_one({"_id": result.inserted_id})
            raise HTTPException(status_code=500, detail="Failed to update company plants array")
    except Exception as e:
        await plants_collection.delete_one({"_id": result.inserted_id})
        raise HTTPException(status_code=500, detail=f"Failed to update company: {str(e)}")

    return {
        "message": f"Plant {plant_id} created successfully for company {company_id}"
    }
    
    
    
    