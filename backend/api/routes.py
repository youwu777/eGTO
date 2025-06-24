"""API routes for the poker solver."""
from fastapi import APIRouter, HTTPException
from models.api_models import SolverRequest, SolverResponse
from services.solver_service import SolverService

router = APIRouter()
solver_service = SolverService()


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "2-Player CFR GTO Solver", "status": "ready"}


@router.post("/solve", response_model=SolverResponse)
async def solve_scenario(request: SolverRequest):
    """Solve 2-player poker scenario using CFR."""
    try:
        return solver_service.solve_scenario(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return solver_service.get_health_status() 