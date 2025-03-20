import asyncio
import json
import os
from pprint import pprint
from dotenv import load_dotenv

from app.models.schemas import ProcessNoteRequest
from app.services.processor import ClinicalNoteProcessor

async def test_processor():
    """Quick test of the processor without starting the API server"""
    print("Testing Clinical Notes Processor...")
    
    # Load test data
    try:
        with open('sample_note.txt', 'r') as file:
            note_text = file.read()
    except FileNotFoundError:
        print("Couldn't find sample_note.txt!")
        return
    
    # Set up a test request
    request = ProcessNoteRequest(
        clinical_note=note_text,
        patient_id="P12345",
        visit_id="V98765"
    )
    
    # Process the note
    processor = ClinicalNoteProcessor()
    try:
        response = await processor.process_note(request)
        
        # Show results
        print("\n=== SUMMARY ===")
        print(response.summary)
        
        print("\n=== EXTRACTED ENTITIES ===")
        entities = response.entities.dict()
        pprint(entities)
        
        # Save for later reference
        with open('processed_result.json', 'w') as f:
            json.dump(response.dict(), f, indent=2, default=str)
        print("\nSaved to processed_result.json")
        
    except Exception as e:
        print(f"Processing failed: {str(e)}")

if __name__ == "__main__":
    # Make sure we have env vars
    load_dotenv()
    
    # Quick env var check
    missing_vars = []
    for var in ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"Error: Missing {', '.join(missing_vars)}")
        print("Create a .env file from .env.example with your Azure OpenAI credentials")
        exit(1)
    
    # Run it
    asyncio.run(test_processor()) 