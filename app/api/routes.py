import logging
from fastapi import APIRouter, HTTPException, Depends

from app.models.schemas import ProcessNoteRequest, ProcessNoteResponse, HealthResponse
from app.services.processor import ClinicalNoteProcessor
from app.utils.monitoring import track_processing_time

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/health", response_model=HealthResponse)
async def health_check():
    # Simple health check for monitoring
    return HealthResponse(
        status="healthy",
        version="0.1.0"
    )

@router.post("/process", response_model=ProcessNoteResponse)
@track_processing_time
async def process_note(request: ProcessNoteRequest):
    # Main endpoint to process clinical notes
    # Takes a note and returns summary + extracted entities
    try:
        processor = ClinicalNoteProcessor()
        response = await processor.process_note(request)
        return response
    except Exception as e:
        # Make sure we don't expose sensitive info in error messages
        logger.error(f"Processing failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process note: {str(e)}"
        ) 