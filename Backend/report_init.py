from datetime import datetime

def initialize_report(company_id: str, plant_id: str, financial_year: str, user_id: str) -> dict:
    """
    Initialize a report dictionary with all question fields set to null, based on the Pydantic schema.

    Args:
        company_id: Unique identifier for the company.
        plant_id: Plant identifier.
        financial_year: Normalized financial year (e.g., '2024_2025').
        user_id: ID of the user creating the report.

    Returns:
        Dictionary representing the initialized report structure.
    """
    return {
        "_id": None,  # MongoDB ObjectId, set to None for Pydantic
        "company_id": company_id,
        "plant_id": plant_id,
        "financial_year": financial_year,
        "created_by": user_id,
        "created_at": datetime.utcnow(),
        "updated_at": None,
        "section_a": {
            "entity_details": {
                "Q1_A": None,  # CIN (str)
                "Q2_A": None,  # Name (str)
                "Q3_A": None,  # Year of Incorporation (int)
                "Q4_A": None,  # Registered Office (str)
                "Q5_A": None,  # Cordres (str)
                "Q6_A": None,  # E-mail (str)
                "Q7_A": None,  # Telephone (str)
                "Q8_A": None,  # Website (str)
                "Q9_A": None,  # Financial Year (str)
                "Q10_A": None,  # Stock Exchange(s) (List[str])
                "Q11_A": None,  # Paid-up Capital (float)
                "Q12_A": None,  # Contact Person (str)
                "Q13_A": None   # Reporting Boundary (str)
            },
            "stock_and_subsidiaries": {
                "Q21a_A": None  # Company Details (dict)
            },
            "products_and_operations": {
                "Q14_A": None,  # Business Activities (dict)
                "Q15_A": None,  # Products/Services Sold (dict)
                "Q16_A": None,  # Locations (dict)
                "Q17a_A": {
                    "markets": None  # List[str]
                },
                "Q17b_A": {
                    "export_percentage": None  # float
                },
                "Q17c_A": {
                    "customer_types": None  # List[str]
                }
            },
            "csr_and_governance": {
                "Q22i_A": None,   # CSR Applicability (dict)
                "Q22ii_A": None,  # Turnover (dict)
                "Q22iii_A": None, # Net Worth (dict)
                "Q23_A": {
                    "grievances_received": None,  # int
                    "grievances_resolved": None   # int
                },
                "Q24_A": None  # Material ESG Issues (dict)
            },
            "employees": {
                "Q18a": {
                    "permanent_employees": {
                        "male": None,  # int
                        "female": None,  # int
                        "other": None  # int
                    },
                    "non_permanent_employees": {
                        "male": None,  # int
                        "female": None,  # int
                        "other": None  # int
                    },
                    "permanent_workers": {
                        "male": None,  # int
                        "female": None,  # int
                        "other": None  # int
                    },
                    "contractual_workers": {
                        "male": None,  # int
                        "female": None,  # int
                        "other": None  # int
                    }
                },
                "Q18b": {
                    "differently_abled_permanent_employees": {
                        "male": None,  # int
                        "female": None,  # int
                        "other": None  # int
                    },
                    "differently_abled_non_permanent_employees": {
                        "male": None,  # int
                        "female": None,  # int
                        "other": None  # int
                    },
                    "differently_abled_permanent_workers": {
                        "male": None,  # int
                        "female": None,  # int
                        "other": None  # int
                    },
                    "differently_abled_contractual_workers": {
                        "male": None,  # int
                        "female": None,  # int
                        "other": None  # int
                    }
                },
                "Q19": {
                    "board_women": None,  # int
                    "management_women": None,  # int
                    "workforce_women": None  # int
                },
                "Q20": {
                    "permanent_employees": {
                        "male": None,  # float
                        "female": None,  # float
                        "other": None  # float
                    },
                    "non_permanent_employees": {
                        "male": None,  # float
                        "female": None,  # float
                        "other": None  # float
                    },
                    "permanent_workers": {
                        "male": None,  # float
                        "female": None,  # float
                        "other": None  # float
                    },
                    "contractual_workers": {
                        "male": None,  # float
                        "female": None,  # float
                        "other": None  # float
                    }
                }
            }
        },
        "section_b": {
            "policy_and_governance": {
                "Q1a_B": {
                    "policies_covered": None  # List[str]
                },
                "Q1b_B": None,  # Policy Approval (str)
                "Q1c_B": None,  # Web Link (str)
                "Q2_B": {
                    "translated_languages": None  # List[str]
                },
                "Q3_B": None,   # Policy Extension (dict)
                "Q4_B": None,   # Codes/Certifications (dict)
                "Q5_B": None,   # Commitments/Goals (dict)
                "Q6_B": None,   # Performance Against Goals (dict)
                "Q7_B": None,   # Director’s Statement (str)
                "Q8_B": None,   # Highest Authority (str)
                "Q9_B": None,   # Sustainability Committee (dict)
                "Q12_B": None   # Reasons for No Policy (str)
            },
            "others": {}
        },
        "section_c": {
            "principle_1": {
                "Q1_P1": None,  # Training on Principles (dict)
                "Q2_P1": None,  # Fines/Penalties (dict)
                "Q3_P1": None,  # Appeals/Revisions (dict)
                "Q4_P1": None,  # Anti-Corruption Policy (dict)
                "Q5_P1": None,  # Disciplinary Actions (dict)
                "Q6_P1": None,  # Conflict of Interest Complaints (dict)
                "Q7_P1": None   # Corrective Actions (dict)
            },
            "principle_2": {
                "Q1_P2": None,  # R&D and Capex (dict)
                "Q2a_P2": None, # Sustainable Sourcing (dict)
                "Q2b_P2": None, # Sustainable Inputs (dict)
                "Q3_P2": None,  # Product Reclamation (dict)
                "Q4_P2": None   # EPR (dict)
            },
            "principle_3": {
                "Q1a_P3": {
                    "health_insurance": None,  # str
                    "leave_policy": None,  # str
                    "wellness_programs": None  # str
                },
                "Q1b_P3": {
                    "health_insurance": None,  # str
                    "leave_policy": None,  # str
                    "wellness_programs": None  # str
                },
                "Q2_P3": {
                    "retirement_benefits_coverage": None,  # str
                    "pension_plan": None                   # str
                },
                "Q3_P3": None,  # Accessibility (dict)
                "Q4_P3": None,  # Equal Opportunity Policy (dict)
                "Q5_P3": None,  # Return to Work and Retention (dict)
                "Q6_P3": {
                    "grievance_mechanism": None,  # str
                    "grievances_resolved": None   # int
                },
                "Q7_P3": None,  # Union Membership (dict)
                "Q8_P3": {
                    "permanent_employees": {"training_hours": None},  # float
                    "non_permanent_employees": {"training_hours": None},  # float
                    "permanent_workers": {"training_hours": None},  # float
                    "contractual_workers": {"training_hours": None}  # float
                },
                "Q9_P3": None,  # Performance Reviews (dict)
                "Q10_P3": None, # Health and Safety System (dict)
                "Q11_P3": {
                    "employees": {
                        "fatalities": None,  # int
                        "injuries": None,  # int
                        "near_misses": None  # int
                    },
                    "workers": {
                        "fatalities": None,  # int
                        "injuries": None,  # int
                        "near_misses": None  # int
                    }
                },
                "Q12_P3": None, # Safe/Healthy Workplace Measures (dict)
                "Q13_P3": {
                    "safety_complaints": None,  # int
                    "resolved": None            # int
                },
                "Q14_P3": None, # Assessments (dict)
                "Q15_P3": None  # Corrective Actions for Safety (dict)
            },
            "principle_4": {
                "Q1_P4": None,  # Stakeholder Identification (dict)
                "Q2_P4": None   # Stakeholder Groups (dict)
            },
            "principle_5": {
                "Q1_P5": {
                    "human_rights_training_hours": None,  # float
                    "employees_trained": None             # str
                },
                "Q2_P5": {"minimum_wage_compliance": None},
                "Q3_P5": {
                    "median_salary_employees": None,  # float
                    "median_salary_workers": None     # float
                },
                "Q4_P5": None,  # Focal Point for Human Rights (dict)
                "Q5_P5": None,  # Grievance Mechanisms (dict)
                "Q6_P5": {
                    "human_rights_complaints": None,  # int
                    "resolved": None                  # int
                },
                "Q7_P5": None,  # Protection for Complainants (dict)
                "Q8_P5": None,  # Human Rights in Contracts (dict)
                "Q9_P5": None,  # Assessments (dict)
                "Q10_P5": None  # Corrective Actions (dict)
            },
            "principle_6": {
                "Q1_P6": None,  # Energy Consumption (dict)
                "Q2_P6": None,  # PAT Scheme (dict)
                "Q3_P6": None,  # Water Usage (dict)
                "Q4_P6": None,  # Air Emissions (dict)
                "Q5_P6": None,  # GHG Emissions (dict)
                "Q6_P6": None,  # GHG Reduction Projects (dict)
                "Q7_P6": None,  # Scope 3 Emissions (dict)
                "Q8_P6": None,  # Waste Management (dict)
                "Q9_P6": None,  # Waste Practices (dict)
                "Q10_P6": None, # Ecologically Sensitive Areas (dict)
                "Q11_P6": None, # Environmental Impact Assessments (dict)
                "Q12_P6": None  # Compliance with Laws (dict)
            },
            "principle_7": {
                "Q1a_P7": None, # Trade Affiliations (dict)
                "Q1b_P7": None, # Top 10 Trade Chambers (dict)
                "Q2_P7": None   # Anti-Competitive Conduct (dict)
            },
            "principle_8": {
                "Q1_P8": None,  # Social Impact Assessments (dict)
                "Q2_P8": None,  # Rehabilitation and Resettlement (dict)
                "Q3_P8": None,  # Community Grievances (dict)
                "Q4_P8": None   # Sourcing from Suppliers (dict)
            },
            "principle_9": {
                "Q1_P9": None,  # Consumer Complaint Mechanisms (dict)
                "Q2_P9": None,  # Product Information Turnover (dict)
                "Q3_P9": None,  # Consumer Complaints (dict)
                "Q4_P9": None,  # Product Recalls (dict)
                "Q5_P9": None,  # Cyber Security Policy (dict)
                "Q6_P9": None   # Corrective Actions (dict)
            }
        }
    }