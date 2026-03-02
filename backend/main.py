"""
Main FastAPI application for College Attendance Analytics Dashboard.
Production-ready with proper configuration, error handling, and documentation.

Now includes:
- Static file serving (CSS, JS)
- Jinja2 template rendering
- Frontend routes (/, /student, /analytics)
- API routes (/api/v1/*)
"""

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database import init_db, engine, Base
from routes import api_router
from schemas import ErrorResponse


# ============== Lifespan Context Manager ==============

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("Starting Attendance Analytics Dashboard API...")
    
    # Initialize database tables
    init_db()
    print("Database initialized")
    
    # Seed sample data if enabled
    if os.getenv("SEED_DATA", "false").lower() == "true":
        from utils.helpers import seed_sample_data
        seed_sample_data()
        print("Sample data seeded")
    
    yield
    
    # Shutdown
    print("Shutting down Attendance Analytics Dashboard API...")
    engine.dispose()


# ============== Application Factory ==============

def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    Factory pattern for better testability and configuration.
    """
    
    # Get the backend directory path
    backend_dir = Path(__file__).parent
    project_root = backend_dir.parent

    app = FastAPI(
        title="College Attendance Analytics Dashboard",
        description="""
        ## Production-Ready Attendance Management System

        This API provides comprehensive attendance tracking and analytics:

        ### Features
        - **Student Management**: CRUD operations for student records
        - **Subject Management**: Course and subject configuration
        - **Attendance Tracking**: Mark and manage daily attendance
        - **Analytics Dashboard**: Real-time attendance statistics
        - **Risk Assessment**: Predict students at risk of shortage
        - **ML Predictions**: Probability of falling below 75%

        ### Authentication
        Currently open for development. Add authentication middleware for production.

        ### Rate Limiting
        Configure rate limiting in production deployment.
        """,
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # ============== Static Files & Templates ==============
    
    # Mount static files (CSS, JS)
    static_dir = project_root / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Setup Jinja2 templates
    templates_dir = backend_dir / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    # ============== Middleware Configuration ==============

    # CORS for frontend access
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:8501,http://localhost:3000,http://127.0.0.1:8501,http://localhost:8000"
        ).split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # ============== Exception Handlers ==============
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors with proper status code."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation error",
                "detail": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request,
        exc: Exception
    ) -> JSONResponse:
        """Handle unexpected errors gracefully."""
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "Internal server error",
                "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
            }
        )
    
    # ============== Include Routers ==============

    app.include_router(api_router, prefix="/api/v1")

    # ============== Frontend Routes ==============

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        """Render the landing page."""
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/student", response_class=HTMLResponse)
    async def student_dashboard(request: Request):
        """Render the student dashboard page."""
        return templates.TemplateResponse("student.html", {"request": request})

    @app.get("/analytics", response_class=HTMLResponse)
    async def class_analytics(request: Request):
        """Render the class analytics page."""
        return templates.TemplateResponse("dashboard.html", {"request": request})

    # ============== Health Check Endpoint ==============
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Health check endpoint for monitoring and load balancers.

        Returns:
            - status: "healthy" if service is running
            - database: "connected" if DB connection works
        """
        try:
            # Test database connection
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            db_status = "connected"
        except Exception:
            db_status = "disconnected"

        return {
            "status": "healthy",
            "database": db_status,
            "version": "1.0.0"
        }

    @app.get("/api", tags=["API Info"])
    async def api_info():
        """API information endpoint."""
        return {
            "name": "College Attendance Analytics Dashboard API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "frontend": "/"
        }
    
    return app


# ============== Application Instance ==============

app = create_app()


# ============== Sample Data Seeder ==============

def seed_sample_data():
    """Legacy seeding kept as a no-op to avoid conflicting with structured seeding."""
    return


if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn for development
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
