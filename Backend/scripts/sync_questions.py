import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import sys
import os

# Add parent directory to path to import from Backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import landing_flow_questions_collection
from models.module_model import Question, QuestionType

async def sync_questions():
    """
    Sync questions from the JSON file to MongoDB.
    """
    try:
        # Read questions from JSON file
        json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               'data', 'questions.json')
        
        print(f"Looking for JSON file at: {json_path}")
        
        with open(json_path, 'r') as f:
            data = json.load(f)

        # Clear existing questions
        await landing_flow_questions_collection.delete_many({})

        # Extract all questions from the JSON structure
        all_questions = []
        for module in data['modules']:
            for submodule in module['submodules']:
                for category in submodule['question_categories']:
                    for q in category['questions']:
                        # Convert to Question model
                        question = Question(
                            question_id=q['question_id'],
                            question=q['question'],
                            type=QuestionType.SUBJECTIVE,  # Default to subjective
                            has_string_value=q.get('has_string_value', False),
                            has_decimal_value=q.get('has_decimal_value', False),
                            has_boolean_value=q.get('has_boolean_value', False),
                            has_link=q.get('has_link', False),
                            has_note=q.get('has_note', False),
                            string_value_required=q.get('string_value_required', False),
                            decimal_value_required=q.get('decimal_value_required', False),
                            boolean_value_required=q.get('boolean_value_required', False),
                            link_required=q.get('link_required', False),
                            note_required=q.get('note_required', False),
                            tab_id=q.get('tab_id'),
                            category_id=category['id'],
                            category_name=category['category_name']
                        )
                        all_questions.append(question.dict())

        # Insert all questions
        if all_questions:
            result = await landing_flow_questions_collection.insert_many(all_questions)
            print(f"Successfully synced {len(result.inserted_ids)} questions")
        else:
            print("No questions found to sync")

    except Exception as e:
        print(f"Error syncing questions: {str(e)}")

if __name__ == "__main__":
    asyncio.run(sync_questions()) 