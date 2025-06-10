import time
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from .schemas import (
    RangeInput, GTOSolution, HealthCheckResponse,
    ErrorResponse, Action, Position
)
from core.solver import GTOSolver
from core.evaluator import HandEvaluator, Range, GameState

router = APIRouter()

# Initialize components
evaluator = HandEvaluator()
solver = GTOSolver(evaluator)

def create_game_state(input_data: RangeInput) -> GameState:
    """Create a GameState object from input data"""
    game_state = GameState(
        effective_stack=input_data.effective_stack,
        pot=input_data.pot
    )
    
    # Set up the board if provided
    if input_data.board:
        game_state.add_to_board(input_data.board)
    
    return game_state

def create_ranges(input_data: RangeInput) -> tuple[Range, Range]:
    """Create Range objects from input data"""
    ip_range = Range()
    oop_range = Range()
    
    # Add hands to ranges with their frequencies
    for hand, freq in input_data.ip_range.items():
        ip_range.add_hand(hand, freq)
    
    for hand, freq in input_data.oop_range.items():
        oop_range.add_hand(hand, freq)
    
    # Normalize frequencies
    ip_range.normalize_weights()
    oop_range.normalize_weights()
    
    return ip_range, oop_range

@router.post(
    "/solve",
    response_model=GTOSolution,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input data"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def solve_gto(input_data: RangeInput) -> Dict[str, Any]:
    """
    Solve for GTO strategies given player ranges and game parameters.
    
    This endpoint takes in the ranges for both players, the current board,
    and other game parameters, then returns the GTO solution.
    """
    try:
        start_time = time.time()
        
        # Set up game state and ranges
        game_state = create_game_state(input_data)
        ip_range, oop_range = create_ranges(input_data)
        
        # Configure solver
        solver.use_gpu = input_data.use_gpu
        
        # Solve for GTO strategies
        solution = solver.solve(
            ip_range=ip_range,
            oop_range=oop_range,
            game_state=game_state,
            max_iterations=input_data.max_iterations,
            accuracy=input_data.accuracy
        )
        
        # Add solving time to the solution
        solution['solving_time'] = time.time() - start_time
        
        return solution
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/health",
    response_model=HealthCheckResponse,
    response_model_exclude_unset=True
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.
    
    Returns the current status of the service and its components.
    """
    import importlib.metadata
    
    try:
        # Try to get package version
        version = importlib.metadata.version("gtosolver")
    except importlib.metadata.PackageNotFoundError:
        version = "0.1.0"  # Default version if package not installed
    
    # Check GPU availability
    try:
        import cupy as cp
        gpu_available = True
    except ImportError:
        gpu_available = False
    
    return {
        "status": "healthy",
        "version": version,
        "gpu_available": gpu_available,
        "gpu_in_use": gpu_available and solver.use_gpu
    }

@router.get(
    "/ranges/default",
    response_model=Dict[str, Dict[str, float]],
    responses={
        200: {"description": "Default range examples"}
    }
)
async def get_default_ranges() -> Dict[str, Dict[str, float]]:
    """
    Get example default ranges for common situations.
    
    Returns example ranges for both IP and OOP players.
    """
    # Example ranges (simplified for demonstration)
    return {
        "ip": {
            "AA": 1.0, "KK": 1.0, "QQ": 1.0, "JJ": 1.0, "TT": 1.0,
            "AKs": 1.0, "AQs": 1.0, "AJs": 0.8, "ATs": 0.7,
            "KQs": 0.9, "KJs": 0.8, "KTs": 0.7,
            "QJs": 0.8, "QTs": 0.7,
            "JTs": 0.8, "J9s": 0.6,
            "T9s": 0.7, "T8s": 0.6,
            "98s": 0.7, "97s": 0.5,
            "87s": 0.7, "86s": 0.5,
            "76s": 0.7, "75s": 0.4,
            "65s": 0.6, "64s": 0.4,
            "54s": 0.6, "53s": 0.4,
            "43s": 0.5, "42s": 0.3,
            "32s": 0.4
        },
        "oop": {
            "AA": 1.0, "KK": 1.0, "QQ": 1.0, "JJ": 1.0, "TT": 1.0, "99": 0.9,
            "88": 0.9, "77": 0.8, "66": 0.7, "55": 0.6,
            "AKs": 1.0, "AQs": 1.0, "AJs": 1.0, "ATs": 0.9, "A9s": 0.7, "A8s": 0.6,
            "AKo": 1.0, "AQo": 1.0, "AJo": 0.9, "KQs": 1.0, "KJs": 0.9, "KTs": 0.8,
            "KQo": 0.9, "QJs": 0.9, "QTs": 0.8, "JTs": 0.9, "J9s": 0.7, "T9s": 0.8,
            "T8s": 0.7, "98s": 0.8, "97s": 0.6, "87s": 0.8, "86s": 0.6, "76s": 0.7,
            "75s": 0.5, "65s": 0.7, "64s": 0.5, "54s": 0.6
        }
    }
