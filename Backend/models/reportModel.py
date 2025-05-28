from pydantic import BaseModel, Field
from typing import Optional, Any, Dict, List
from datetime import datetime
from bson import ObjectId

from models.base import PyObjectId

# Question-specific models for questions with subparts
class EmployeeType(BaseModel):
    male: Optional[int] = None
    female: Optional[int] = None
    other: Optional[int] = None

class Q18aModel(BaseModel):
    permanent_employees: Optional[EmployeeType] = None
    non_permanent_employees: Optional[EmployeeType] = None
    permanent_workers: Optional[EmployeeType] = None
    contractual_workers: Optional[EmployeeType] = None

class Q18bModel(BaseModel):
    differently_abled_permanent_employees: Optional[EmployeeType] = None
    differently_abled_non_permanent_employees: Optional[EmployeeType] = None
    differently_abled_permanent_workers: Optional[EmployeeType] = None
    differently_abled_contractual_workers: Optional[EmployeeType] = None

class Q19Model(BaseModel):
    board_women: Optional[int] = None
    management_women: Optional[int] = None
    workforce_women: Optional[int] = None

class TurnoverType(BaseModel):
    male: Optional[float] = None
    female: Optional[float] = None
    other: Optional[float] = None

class Q20Model(BaseModel):
    permanent_employees: Optional[TurnoverType] = None
    non_permanent_employees: Optional[TurnoverType] = None
    permanent_workers: Optional[TurnoverType] = None
    contractual_workers: Optional[TurnoverType] = None

class Q1aP3Model(BaseModel):
    health_insurance: Optional[str] = None
    leave_policy: Optional[str] = None
    wellness_programs: Optional[str] = None

class Q1bP3Model(BaseModel):
    health_insurance: Optional[str] = None
    leave_policy: Optional[str] = None
    wellness_programs: Optional[str] = None

class Q2P3Model(BaseModel):
    retirement_benefits_coverage: Optional[str] = None
    pension_plan: Optional[str] = None

class Q6P3Model(BaseModel):
    grievance_mechanism: Optional[str] = None
    grievances_resolved: Optional[int] = None

class TrainingHours(BaseModel):
    training_hours: Optional[float] = None

class Q8P3Model(BaseModel):
    permanent_employees: Optional[TrainingHours] = None
    non_permanent_employees: Optional[TrainingHours] = None
    permanent_workers: Optional[TrainingHours] = None
    contractual_workers: Optional[TrainingHours] = None

class SafetyMetrics(BaseModel):
    fatalities: Optional[int] = None
    injuries: Optional[int] = None
    near_misses: Optional[int] = None

class Q11P3Model(BaseModel):
    employees: Optional[SafetyMetrics] = None
    workers: Optional[SafetyMetrics] = None

class Q13P3Model(BaseModel):
    safety_complaints: Optional[int] = None
    resolved: Optional[int] = None

class Q1P5Model(BaseModel):
    human_rights_training_hours: Optional[float] = None
    employees_trained: Optional[str] = None

class Q3P5Model(BaseModel):
    median_salary_employees: Optional[float] = None
    median_salary_workers: Optional[float] = None

class Q6P5Model(BaseModel):
    human_rights_complaints: Optional[int] = None
    resolved: Optional[int] = None

class Q1aBModel(BaseModel):
    policies_covered: Optional[List[str]] = None

class Q2BModel(BaseModel):
    translated_languages: Optional[List[str]] = None

class Q17aAModel(BaseModel):
    markets: Optional[List[str]] = None

class Q17bAModel(BaseModel):
    export_percentage: Optional[float] = None

class Q17cAModel(BaseModel):
    customer_types: Optional[List[str]] = None

class Q23AModel(BaseModel):
    grievances_received: Optional[int] = None
    grievances_resolved: Optional[int] = None

# Update log model
class UpdateLog(BaseModel):
    question_id: str
    updated_by: str
    updated_at: datetime
    schema_path: str
    previous_value: Optional[str] = None
    new_value: Optional[str] = None

# Pydantic model for question update
class QuestionUpdate(BaseModel):
    question_id: str
    value: Any

# Section A sub-structures
class EntityDetails(BaseModel):
    Q1_A: Optional[str] = None  # CIN
    Q2_A: Optional[str] = None  # Name
    Q3_A: Optional[int] = None  # Year of Incorporation
    Q4_A: Optional[str] = None  # Registered Office
    Q5_A: Optional[str] = None  # Corporate Address
    Q6_A: Optional[str] = None  # E-mail
    Q7_A: Optional[str] = None  # Telephone
    Q8_A: Optional[str] = None  # Website
    Q9_A: Optional[str] = None  # Financial Year
    Q10_A: Optional[List[str]] = None  # Stock Exchange(s)
    Q11_A: Optional[float] = None  # Paid-up Capital
    Q12_A: Optional[str] = None  # Contact Person
    Q13_A: Optional[str] = None  # Reporting Boundary

class StockAndManagement(BaseModel):
    Q21a_A: Optional[Dict[str, Any]] = None  # Company Details

class ProductsAndOperations(BaseModel):
    Q14_A: Optional[Dict[str, Any]] = None  # Business Activities
    Q15_A: Optional[Dict[str, Any]] = None  #
    Q16_A: Optional[Dict[str, Any]] = None  # Locations
    Q17a_A: Optional[Q17aAModel] = None  # Markets Served
    Q17b_A: Optional[Q17bAModel] = None  # Export Contribution
    Q17c_A: Optional[Q17cAModel] = None  # Customer Types

class CSRAndGovernance(BaseModel):
    Q22i_A: Optional[Dict[str, Any]] = None  # CSR Applicability
    Q22ii_A: Optional[Dict[str, Any]] = None  # Turnover
    Q22iii_A: Optional[Dict[str, Any]] = None  # Net Worth
    Q23_A: Optional[Q23AModel] = None  # Complaints/Grievances
    Q24_A: Optional[Dict[str, Any]] = None  # Material ESG Issues

class Employees(BaseModel):
    Q18a: Optional[Q18aModel] = None  # Employees and Workers
    Q18b: Optional[Q18bModel] = None  # Differently Abled Employees and Workers
    Q19: Optional[Q19Model] = None  # Participation/Inclusion of Women
    Q20: Optional[Q20Model] = None  # Turnover Rate

class SectionA(BaseModel):
    entity_details: Optional[EntityDetails] = None
    stock_and_management: Optional[StockAndManagement] = None
    products_and_operations: Optional[ProductsAndOperations] = None
    csr_and_governance: Optional[CSRAndGovernance] = None
    employees: Optional[Employees] = None

# Section B sub-structures
class PolicyAndGovernance(BaseModel):
    Q1a_B: Optional[Q1aBModel] = None  # Policy Coverage
    Q1b_B: Optional[str] = None  # Policy Approval
    Q1c_B: Optional[str] = None  # Web Link
    Q2_B: Optional[Q2BModel] = None  # Policy Translation
    Q3_B: Optional[Dict[str, Any]] = None  # Policy Extension
    Q4_B: Optional[Dict[str, Any]] = None  # Codes/Certifications
    Q5_B: Optional[Dict[str, Any]] = None  # Commitments/Goals
    Q6_B: Optional[Dict[str, Any]] = None  # Performance Against Goals
    Q7_B: Optional[str] = None  # Director’s Statement
    Q8_B: Optional[str] = None  # Highest Authority
    Q9_B: Optional[Dict[str, Any]] = None  # Sustainability Committee
    Q12_B: Optional[str] = None  # Reasons for No Policy

class SectionB(BaseModel):
    policy_and_governance: Optional[PolicyAndGovernance] = None
    others: Optional[Dict[str, Any]] = None

# Section C sub-structures
class Principle1(BaseModel):
    Q1_P1: Optional[Dict[str, Any]] = None  # Training on Principles
    Q2_P1: Optional[Dict[str, Any]] = None  # Fines/Penalties
    Q3_P1: Optional[Dict[str, Any]] = None  # Appeals/Revisions
    Q4_P1: Optional[Dict[str, Any]] = None  # Anti-Corruption Policy
    Q5_P1: Optional[Dict[str, Any]] = None  # Disciplinary Actions
    Q6_P1: Optional[Dict[str, Any]] = None  # Conflict of Interest Complaints
    Q7_P1: Optional[Dict[str, Any]] = None  # Corrective Actions

class Principle2(BaseModel):
    Q1_P2: Optional[Dict[str, Any]] = None  # R&D and Capex
    Q2a_P2: Optional[Dict[str, Any]] = None  # Sustainable Sourcing
    Q2b_P2: Optional[Dict[str, Any]] = None  # Sustainable Inputs
    Q3_P2: Optional[Dict[str, Any]] = None  # Product Reclamation
    Q4_P2: Optional[Dict[str, Any]] = None  # EPR

class Principle3(BaseModel):
    Q1a_P3: Optional[Q1aP3Model] = None  # Employee Well-Being Measures
    Q1b_P3: Optional[Q1bP3Model] = None  # Worker Well-Being Measures
    Q2_P3: Optional[Q2P3Model] = None  # Retirement Benefits
    Q3_P3: Optional[Dict[str, Any]] = None  # Accessibility
    Q4_P3: Optional[Dict[str, Any]] = None  # Equal Opportunity Policy
    Q5_P3: Optional[Dict[str, Any]] = None  # Return to Work and Retention
    Q6_P3: Optional[Q6P3Model] = None  # Grievance Mechanisms
    Q7_P3: Optional[Dict[str, Any]] = None  # Union Membership
    Q8_P3: Optional[Q8P3Model] = None  # Training Details
    Q9_P3: Optional[Dict[str, Any]] = None  # Performance Reviews
    Q10_P3: Optional[Dict[str, Any]] = None  # Health and Safety System
    Q11_P3: Optional[Q11P3Model] = None  # Safety Incidents
    Q12_P3: Optional[Dict[str, Any]] = None  # Safe/Healthy Workplace Measures
    Q13_P3: Optional[Q13P3Model] = None  # Complaints on Conditions/Safety
    Q14_P3: Optional[Dict[str, Any]] = None  # Assessments
    Q15_P3: Optional[Dict[str, Any]] = None  # Corrective Actions for Safety

class Principle4(BaseModel):
    Q1_P4: Optional[Dict[str, Any]] = None  # Stakeholder Identification
    Q2_P4: Optional[Dict[str, Any]] = None  # Stakeholder Groups

class Q2P5Data(BaseModel):
    minimum_wage_compliance: Optional[bool] = None

class Principle5(BaseModel):
    Q1_P5: Optional[Q1P5Model] = None  # Human Rights Training
    Q2_P5: Optional[Q2P5Data] = None
    Q3_P5: Optional[Q3P5Model] = None  # Remuneration Details
    Q4_P5: Optional[Dict[str, Any]] = None  # Focal Point for Human Rights
    Q5_P5: Optional[Dict[str, Any]] = None  # Grievance Mechanisms
    Q6_P5: Optional[Q6P5Model] = None  # Complaints on Human Rights
    Q7_P5: Optional[Dict[str, Any]] = None  # Protection for Complainants
    Q8_P5: Optional[Dict[str, Any]] = None  # Human Rights in Contracts
    Q9_P5: Optional[Dict[str, Any]] = None  # Assessments
    Q10_P5: Optional[Dict[str, Any]] = None  # Corrective Actions

class Principle6(BaseModel):
    Q1_P6: Optional[Dict[str, Any]] = None  # Energy Consumption
    Q2_P6: Optional[Dict[str, Any]] = None  # PAT Scheme
    Q3_P6: Optional[Dict[str, Any]] = None  # Water Usage
    Q4_P6: Optional[Dict[str, Any]] = None  # Air Emissions
    Q5_P6: Optional[Dict[str, Any]] = None  # GHG Emissions
    Q6_P6: Optional[Dict[str, Any]] = None  # GHG Reduction Projects
    Q7_P6: Optional[Dict[str, Any]] = None  # Scope 3 Emissions
    Q8_P6: Optional[Dict[str, Any]] = None  # Waste Management
    Q9_P6: Optional[Dict[str, Any]] = None  # Waste Practices
    Q10_P6: Optional[Dict[str, Any]] = None  # Ecologically Sensitive Areas
    Q11_P6: Optional[Dict[str, Any]] = None  # Environmental Impact Assessments
    Q12_P6: Optional[Dict[str, Any]] = None  # Compliance with Laws

class Principle7(BaseModel):
    Q1a_P7: Optional[Dict[str, Any]] = None  # Trade Affiliations
    Q1b_P7: Optional[Dict[str, Any]] = None  # Top 10 Trade Chambers
    Q2_P7: Optional[Dict[str, Any]] = None  # Anti-Competitive Conduct

class Principle8(BaseModel):
    Q1_P8: Optional[Dict[str, Any]] = None  # Social Impact Assessments
    Q2_P8: Optional[Dict[str, Any]] = None  # Rehabilitation and Resettlement
    Q3_P8: Optional[Dict[str, Any]] = None  # Community Grievances
    Q4_P8: Optional[Dict[str, Any]] = None  # Sourcing from Suppliers

class Principle9(BaseModel):
    Q1_P9: Optional[Dict[str, Any]] = None  # Consumer Complaint Mechanisms
    Q2_P9: Optional[Dict[str, Any]] = None  # Product Information Turnover
    Q3_P9: Optional[Dict[str, Any]] = None  # Consumer Complaints
    Q4_P9: Optional[Dict[str, Any]] = None  # Product Recalls
    Q5_P9: Optional[Dict[str, Any]] = None  # Cyber Security Policy
    Q6_P9: Optional[Dict[str, Any]] = None  # Corrective Actions

class SectionC(BaseModel):
    principle_1: Optional[Principle1] = None
    principle_2: Optional[Principle2] = None
    principle_3: Optional[Principle3] = None
    principle_4: Optional[Principle4] = None
    principle_5: Optional[Principle5] = None
    principle_6: Optional[Principle6] = None
    principle_7: Optional[Principle7] = None
    principle_8: Optional[Principle8] = None
    principle_9: Optional[Principle9] = None

# Modules sub-structures
class WorkforceDetails(BaseModel):
    Q18a: Optional[Q18aModel] = None
    Q18b: Optional[Q18bModel] = None
    Q19: Optional[Q19Model] = None
    Q20: Optional[Q20Model] = None

class EmployeeWellbeing(BaseModel):
    Q1a_P3: Optional[Q1aP3Model] = None
    Q1b_P3: Optional[Q1bP3Model] = None
    Q2_P3: Optional[Q2P3Model] = None
    Q3_P3: Optional[Dict[str, Any]] = None
    Q4_P3: Optional[Dict[str, Any]] = None
    Q5_P3: Optional[Dict[str, Any]] = None
    Q6_P3: Optional[Q6P3Model] = None
    Q7_P3: Optional[Dict[str, Any]] = None
    Q8_P3: Optional[Q8P3Model] = None
    Q9_P3: Optional[Dict[str, Any]] = None
    Q10_P3: Optional[Dict[str, Any]] = None
    Q11_P3: Optional[Q11P3Model] = None
    Q12_P3: Optional[Dict[str, Any]] = None
    Q13_P3: Optional[Q13P3Model] = None
    Q14_P3: Optional[Dict[str, Any]] = None
    Q15_P3: Optional[Dict[str, Any]] = None

class HumanRights(BaseModel):
    Q1_P5: Optional[Q1P5Model] = None
    Q2_P5: Optional[Q2P5Data] = None
    Q3_P5: Optional[Q3P5Model] = None
    Q4_P5: Optional[Dict[str, Any]] = None
    Q5_P5: Optional[Dict[str, Any]] = None
    Q6_P5: Optional[Q6P5Model] = None
    Q7_P5: Optional[Dict[str, Any]] = None
    Q8_P5: Optional[Dict[str, Any]] = None
    Q9_P5: Optional[Dict[str, Any]] = None
    Q10_P5: Optional[Dict[str, Any]] = None

class HRModule(BaseModel):
    workforce_details: Optional[WorkforceDetails] = None
    employee_wellbeing: Optional[EmployeeWellbeing] = None
    human_rights: Optional[HumanRights] = None
    retirement: Optional[Dict[str, Any]] = None
    others: Optional[Dict[str, Any]] = None

class LegalPolicyAndGovernance(BaseModel):
    Q1a_B: Optional[Q1aBModel] = None
    Q1b_B: Optional[str] = None
    Q1c_B: Optional[str] = None
    Q2_B: Optional[Q2BModel] = None
    Q3_B: Optional[Dict[str, Any]] = None
    Q4_B: Optional[Dict[str, Any]] = None
    Q5_B: Optional[Dict[str, Any]] = None
    Q6_B: Optional[Dict[str, Any]] = None
    Q7_B: Optional[str] = None
    Q8_B: Optional[str] = None
    Q9_B: Optional[Dict[str, Any]] = None
    Q12_B: Optional[str] = None

class LegalModule(BaseModel):
    policy_and_governance: Optional[LegalPolicyAndGovernance] = None
    ethical_conduct: Optional[Dict[str, Any]] = None
    policy_advocacy: Optional[Dict[str, Any]] = None
    others: Optional[Dict[str, Any]] = None

class FinanceModule(BaseModel):
    products_and_services: Optional[Dict[str, Any]] = None
    csr: Optional[Dict[str, Any]] = None
    inclusive_growth: Optional[Dict[str, Any]] = None
    transparency_and_governance: Optional[Dict[str, Any]] = None
    consumer_responsibility: Optional[Dict[str, Any]] = None

class AdminModule(BaseModel):
    entity_details: Optional[EntityDetails] = None
    operations: Optional[Dict[str, Any]] = None
    corporate_structure: Optional[Dict[str, Any]] = None
    stakeholder_engagement: Optional[Dict[str, Any]] = None

class EnvironmentModule(BaseModel):
    sustainable_products: Optional[Dict[str, Any]] = None
    energy_management: Optional[Dict[str, Any]] = None
    water_and_resources: Optional[Dict[str, Any]] = None
    environmental_compliance: Optional[Dict[str, Any]] = None

class Modules(BaseModel):
    workforce: Optional[HRModule] = None
    legal: Optional[LegalModule] = None
    finance: Optional[FinanceModule] = None
    admin: Optional[AdminModule] = None
    environment: Optional[EnvironmentModule] = None

class Report(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    company_id: str
    plant_id: str
    financial_year: str
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    section_a: Optional[SectionA] = None
    section_b: Optional[SectionB] = None
    section_c: Optional[SectionC] = None
    #modules: Optional[Modules] = None
    updates: Optional[List[UpdateLog]] = None  # Added for update_report compatibility

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }
        allow_population_by_field_name = True