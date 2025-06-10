import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import uvicorn

# Import API endpoints
from api.endpoints import router as api_router

# Load environment variables
load_dotenv()

def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    # Load environment variables
    load_dotenv()
    
    # Initialize FastAPI app
    app = FastAPI(
        title="GTO Poker Solver API",
        description="""
        A high-performance Texas Hold'em GTO solver with GPU acceleration.
        
        This API provides endpoints for solving GTO strategies for Texas Hold'em poker.
        It supports range vs. range analysis with configurable game parameters.
        """,
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include API router
    app.include_router(api_router, prefix="/api")

    # Custom exception handlers
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"},
        )

    # Health check endpoint
    @app.get("/")
    async def root():
        return {
            "message": "GTO Poker Solver API",
            "status": "running",
            "documentation": "/docs"
        }

    return app

# Create the application
app = create_application()

# Configure OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="GTO Poker Solver API",
        version="0.1.0",
        description="A high-performance Texas Hold'em GTO solver with GPU acceleration",
        routes=app.routes,
    )
    
    # Add custom documentation
    openapi_schema["info"]["contact"] = {
        "name": "GTO Solver Team",
        "email": "support@gtosolver.com"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
