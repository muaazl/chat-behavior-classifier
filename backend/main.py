from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as analysis_router, coordinator
from app.middleware.privacy_handler import PrivacyCleanupMiddleware
from app.core.logger_config import setup_privacy_logging
import logging
import uuid
import time
from datetime import datetime
from contextlib import asynccontextmanager
import os
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

# Initialize Privacy Logging
setup_privacy_logging(level=logging.INFO)
logger = logging.getLogger("api_main")

limiter = Limiter(key_func=get_remote_address)

class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Warm up ML models
    logger.info("Starting Moodrae Engine")
    coordinator.warm_up()
    yield
    # Shutdown: Clean up if needed
    logger.info("Shutting down Moodrae Engine")
    coordinator.shutdown()

app = FastAPI(
    title="Moodrae - Analyzer Service",
    description="Privacy-first, local-only NLP engine for WhatsApp chat analysis.",
    version="1.0.0",
    lifespan=lifespan
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware 
# In production on Hugging Face, set the CORS_ORIGINS env var
default_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://moodrae.vercel.app"
]

allowed_origins_env = os.getenv("CORS_ORIGINS", "")
allowed_origins = allowed_origins_env.split(",") if allowed_origins_env else default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Privacy Middleware (Cleans up memory after each request)
app.add_middleware(PrivacyCleanupMiddleware)

# Request ID Middleware
app.add_middleware(RequestIDMiddleware)

# API Routes
app.include_router(analysis_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Minimal health check to verify backend is up."""
    return {
        "status": "online",
        "service": "Moodrae Engine",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

if __name__ == "__main__":
    import uvicorn
    # Respect PORT env var if provided (useful for Docker/HF local testing)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, access_log=True)