"""Routes package for API endpoints."""

from fastapi import APIRouter

from .students import router as students_router
from .subjects import router as subjects_router
from .attendance import router as attendance_router
from .analytics import router as analytics_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(students_router)
api_router.include_router(subjects_router)
api_router.include_router(attendance_router)
api_router.include_router(analytics_router)

__all__ = ['api_router']
