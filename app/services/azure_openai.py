import json
import logging
import time
from typing import Dict, Any, Optional, List

import openai
import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config.settings import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_VERSION,
    AZURE_OPENAI_DEPLOYMENT_SUMMARY,
    AZURE_OPENAI_DEPLOYMENT_EXTRACTION,
)

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    def __init__(self):
        self.api_key = AZURE_OPENAI_API_KEY
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.api_version = AZURE_OPENAI_API_VERSION
        self.summary_deployment = AZURE_OPENAI_DEPLOYMENT_SUMMARY
        self.extraction_deployment = AZURE_OPENAI_DEPLOYMENT_EXTRACTION
        
        # Setup Azure OpenAI connection
        openai.api_type = "azure"
        openai.api_key = self.api_key
        openai.api_base = self.endpoint
        openai.api_version = self.api_version
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def generate_summary(self, clinical_note: str) -> str:
        # Generate summary from clinical notes
        start_time = time.time()
        try:
            # This prompt works well based on my testing
            system_prompt = """Summarize this clinical note like a medical professional would.
            Include the most important info:
            - Patient details
            - Key diagnoses
            - Major findings
            - What the treatment plan is
            - Follow-up plan
            
            Keep it focused on medical details. Skip the administrative stuff."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Summarize this note: {clinical_note}"}
            ]
            
            # Call Azure OpenAI
            response = openai.ChatCompletion.create(
                deployment_id=self.summary_deployment,
                messages=messages,
                temperature=0.3,  # found this works best
                max_tokens=500,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Log for performance tracking
            duration = time.time() - start_time
            logger.info(f"Summary done in {duration:.2f}s, length: {len(summary)} chars")
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed generating summary: {str(e)}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    def extract_entities(self, clinical_note: str) -> Dict[str, Any]:
        # Extract medical entities from clinical note
        start_time = time.time()
        try:
            # Prompt that gets decent extraction results
            system_prompt = """Extract the key medical info from this clinical note as structured data.
            I need:
            - Medications (with dosage/frequency/route when available)
            - Diagnoses (with status if mentioned)
            - Procedures (with dates if mentioned)
            - Allergies
            - Vital signs
            
            Return as JSON that looks like:
            {
                "medications": [{"name": "med name", "dosage": "dose", "frequency": "how often", "route": "how given"}],
                "diagnoses": [{"condition": "diagnosis", "status": "current status", "certainty": "confirmed/suspected"}],
                "procedures": [{"name": "procedure name", "date": "when done", "status": "completed/planned"}],
                "allergies": ["allergy1", "allergy2"],
                "vitals": {"temp": "value", "bp": "value", "hr": "value"}
            }
            
            Only include fields that actually appear in the note."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract structured data from: {clinical_note}"}
            ]
            
            response = openai.ChatCompletion.create(
                deployment_id=self.extraction_deployment,
                messages=messages,
                temperature=0.1,  # need precise extraction
                max_tokens=1000,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Sometimes the model adds explanatory text around the JSON
            # Need to handle that case
            try:
                entities = self._extract_json_from_text(extracted_text)
            except Exception as e:
                logger.warning(f"JSON extraction issue: {str(e)}")
                # Try the whole thing as JSON
                entities = json.loads(extracted_text)
                
            # Track performance
            duration = time.time() - start_time
            entity_count = sum(len(entities.get(k, [])) for k in ['medications', 'diagnoses', 'procedures', 'allergies'])
            logger.info(f"Extracted {entity_count} entities in {duration:.2f}s")
            
            return entities
            
        except Exception as e:
            logger.error(f"Failed extracting entities: {str(e)}")
            raise
    
    def _extract_json_from_text(self, text: str) -> Dict[str, Any]:
        """Get JSON from text that might have extra stuff around it"""
        try:
            # First try parsing the whole thing
            return json.loads(text)
        except json.JSONDecodeError:
            # If that fails, try to find JSON between { and }
            start_idx = text.find('{')
            end_idx = text.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > 0:
                json_str = text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("Couldn't find valid JSON in the response") 