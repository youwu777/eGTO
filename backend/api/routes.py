"""API routes for the comprehensive poker solver."""
from fastapi import APIRouter, HTTPException
from models.api_models import (
    SolverRequest, SolverResponse, PostflopRequest, PostflopResponse,
    GameConfigRequest, GameConfigResponse
)
from services.solver_service import SolverService
from services.comprehensive_solver_service import ComprehensiveSolverService

router = APIRouter()
solver_service = SolverService()
comprehensive_solver_service = ComprehensiveSolverService()


@router.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Comprehensive 2-Player CFR GTO Solver", 
        "version": "2.0.0",
        "status": "ready",
        "features": [
            "Full postflop game tree support",
            "Monte Carlo equity calculations",
            "User-configurable bet sizes",
            "User-configurable max bets per street",
            "Convergence tracking",
            "Board texture analysis",
            "Hand strength analysis",
            "Game configuration validation"
        ]
    }


@router.post("/solve", response_model=SolverResponse)
async def solve_scenario(request: SolverRequest):
    """Solve 2-player poker scenario using basic CFR (legacy endpoint)."""
    try:
        return solver_service.solve_scenario(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/solve/comprehensive", response_model=SolverResponse)
async def solve_comprehensive_scenario(request: SolverRequest):
    """Solve comprehensive 2-player poker scenario with full postflop support."""
    try:
        return comprehensive_solver_service.solve_comprehensive_scenario(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/postflop", response_model=PostflopResponse)
async def analyze_postflop_spot(request: PostflopRequest):
    """Analyze specific postflop spot with detailed hand analysis."""
    try:
        return comprehensive_solver_service.analyze_postflop_spot(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/config", response_model=GameConfigResponse)
async def validate_game_config(request: GameConfigRequest):
    """Validate game configuration and estimate computational requirements."""
    try:
        return comprehensive_solver_service.validate_game_config(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return solver_service.get_health_status()


@router.get("/health/comprehensive")
async def comprehensive_health_check():
    """Comprehensive solver health check."""
    return comprehensive_solver_service.get_solver_status()


@router.get("/info")
async def solver_info():
    """Get solver information and capabilities."""
    return {
        "solver_type": "Comprehensive CFR GTO Solver",
        "version": "2.0.0",
        "capabilities": {
            "preflop": True,
            "postflop": True,
            "user_configurable_bet_sizes": True,
            "user_configurable_max_bets": True,
            "multiple_bet_sizes": True,
            "convergence_tracking": True,
            "monte_carlo_equity": True,
            "board_texture_analysis": True,
            "hand_strength_analysis": True,
            "range_vs_range": True,
            "game_config_validation": True
        },
        "default_bet_sizes": [0.33, 0.5, 0.75, 1.0, 1.5, 2.0],
        "default_max_bets_per_street": {
            "preflop": 4,
            "flop": 3,
            "turn": 2,
            "river": 1
        },
        "max_iterations": 1000000,
        "convergence_threshold": 0.001,
        "monte_carlo_simulations": 10000
    } 