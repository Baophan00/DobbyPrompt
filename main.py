import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
from api.endpoints import router as api_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Fireworks AI Agent API", version="1.0.0")

# CORS middleware - SỬA ĐOẠN NÀY
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://0.0.0.0:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Fireworks AI Agent API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_provider": os.getenv("MODEL_PROVIDER", "fireworks")}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Using model provider: {os.getenv('MODEL_PROVIDER', 'fireworks')}")
    
    uvicorn.run(app, host=host, port=port)