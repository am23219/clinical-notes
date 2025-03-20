import logging
import uuid
from typing import Dict, Any, Optional

from app.models.schemas import ProcessNoteRequest, ProcessNoteResponse, ExtractedEntities
from app.services.azure_openai import AzureOpenAIService

logger = logging.getLogger(__name__)

class ClinicalNoteProcessor:
    def __init__(self):
        self.openai_service = AzureOpenAIService()
    
    async def process_note(self, request: ProcessNoteRequest) -> ProcessNoteResponse:
        # Process a clinical note to generate summary and extract entities
        request_id = str(uuid.uuid4())
        logger.info(f"Processing note for patient {request.patient_id}, request ID: {request_id}")
        
        try:
            # Get both the summary and entities in sequence
            # Would be nice to parallelize these someday
            summary = self.openai_service.generate_summary(request.clinical_note)
            
            # Extract structured entities
            entities_dict = self.openai_service.extract_entities(request.clinical_note)
            
            # Convert raw dict to Pydantic model for validation
            entities = ExtractedEntities(
                medications=entities_dict.get("medications", []),
                diagnoses=entities_dict.get("diagnoses", []),
                procedures=entities_dict.get("procedures", []),
                allergies=entities_dict.get("allergies", []),
                vitals=entities_dict.get("vitals", {})
            )
            
            # Return everything in a structured response
            response = ProcessNoteResponse(
                request_id=request_id,
                patient_id=request.patient_id,
                visit_id=request.visit_id,
                summary=summary,
                entities=entities
            )
            
            logger.info(f"Finished processing note {request_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error in processing note {request_id}: {str(e)}")
            raise 