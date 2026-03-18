from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.api.auth import router as auth_router
from backend.api.user import router as user_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(user_router)


# Health check endpoint (outside /api/v1 prefix for easy access)
health_router = APIRouter()


@health_router.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestration."""
    return JSONResponse(content={"status": "healthy"}, status_code=200)
