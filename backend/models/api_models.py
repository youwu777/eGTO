"""API request and response models."""
from pydantic import BaseModel, Field
from typing import Dict


class SolverRequest(BaseModel):
    """Request model for solver endpoint."""
    oop_range: str = Field(..., description="OOP range string (e.g., 'AA-77,AKs-ATs,AKo-AJo')")
    ip_range: str = Field(..., description="IP range string")
    starting_stack: float = Field(..., gt=0, description="Starting stack size")
    pot_size: float = Field(..., gt=0, description="Initial pot size")
    bet_size: float = Field(..., gt=0, description="Bet size (as fraction of pot)")
    max_bets: int = Field(..., ge=1, le=4, description="Maximum number of bets/raises")


class SolverResponse(BaseModel):
    """Response model for solver endpoint."""
    oop_strategy: Dict[str, Dict[str, float]]
    ip_strategy: Dict[str, Dict[str, float]]
    training_iterations: int
    computation_time: float 