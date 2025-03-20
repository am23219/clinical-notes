import os
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Logging setup
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# App settings
APP_ENV = os.getenv("APP_ENV", "development")
DEBUG = APP_ENV == "development"

# Azure OpenAI settings - make sure these are in your .env file!
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")

# Model deployments - change these to match your Azure deployments
AZURE_OPENAI_DEPLOYMENT_SUMMARY = os.getenv("AZURE_OPENAI_DEPLOYMENT_SUMMARY")
AZURE_OPENAI_DEPLOYMENT_EXTRACTION = os.getenv("AZURE_OPENAI_DEPLOYMENT_EXTRACTION")

# Check if we have everything we need
def verify_settings():
    missing = []
    
    # Critical settings that we absolutely need
    if not AZURE_OPENAI_API_KEY:
        missing.append("AZURE_OPENAI_API_KEY")
    if not AZURE_OPENAI_ENDPOINT:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_DEPLOYMENT_SUMMARY:
        missing.append("AZURE_OPENAI_DEPLOYMENT_SUMMARY")
    if not AZURE_OPENAI_DEPLOYMENT_EXTRACTION:
        missing.append("AZURE_OPENAI_DEPLOYMENT_EXTRACTION")
    
    if missing:
        error_msg = f"Missing env vars: {', '.join(missing)}"
        logger.error(error_msg)
        if APP_ENV != "development":
            # In prod, fail fast. In dev, just warn
            raise EnvironmentError(error_msg)
        else:
            logger.warning("⚠️ Running in dev mode with missing settings - things will break!")

# Make sure we have our settings
verify_settings() 