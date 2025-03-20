import logging
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.routes import router as api_router
from app.config.settings import DEBUG

# Setup logging
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Clinical Notes Summarizer & Insights Extractor",
    description="Microservice for processing clinical notes to extract structured info",
    version="0.1.0",
    debug=DEBUG,
)

# CORS setup - change this for production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Lock this down before prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(api_router, prefix="/api")

# Handle validation errors nicely
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        })
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )

@app.get("/")
async def root():
    # Root endpoint with basic info
    return {"message": "Clinical Notes API - go to /docs for documentation"}

# App startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Clinical Notes API")
    
# App shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Clinical Notes API") 