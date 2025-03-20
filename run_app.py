import os
import uvicorn
from dotenv import load_dotenv

# Get our environment variables
load_dotenv()

# Server config
PORT = int(os.getenv("PORT", "8000"))
HOST = os.getenv("HOST", "0.0.0.0")
RELOAD = os.getenv("APP_ENV", "development") == "development"

if __name__ == "__main__":
    print(f"Starting API server on {HOST}:{PORT}")
    print(f"API docs: http://localhost:{PORT}/docs")
    print(f"Debug mode: {'enabled' if RELOAD else 'disabled'}")
    
    # Make sure we have the basics
    if not os.getenv("AZURE_OPENAI_API_KEY") or not os.getenv("AZURE_OPENAI_ENDPOINT"):
        print("⚠️  Warning: Missing Azure OpenAI credentials!")
        print("Create a .env file from .env.example with your credentials")
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
    ) 