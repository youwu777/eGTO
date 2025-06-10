from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

class Action(str, Enum):
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"

class Position(str, Enum):
    IP = "ip"  # In Position
    OOP = "oop"  # Out of Position

class RangeInput(BaseModel):
    """Input for GTO solver"""
    ip_range: Dict[str, float] = Field(
        ...,
        description="In-position player's range as a dictionary of hand:frequency pairs"
    )
    oop_range: Dict[str, float] = Field(
        ...,
        description="Out-of-position player's range as a dictionary of hand:frequency pairs"
    )
    board: List[str] = Field(
        default_factory=list,
        description="Community cards (e.g., [\"As\", \"Kd\", \"Qh\"])"
    )
    effective_stack: float = Field(
        100.0,
        description="Effective stack size in big blinds"
    )
    pot: float = Field(
        1.0,
        description="Current pot size in big blinds"
    )
    bet_sizes: List[float] = Field(
        default_factory=lambda: [0.5, 1.0, 2.0],
        description="Available bet sizes as fractions of pot"
    )
    max_iterations: int = Field(
        100,
        description="Maximum number of iterations for the solver"
    )
    accuracy: float = Field(
        0.001,
        description="Convergence threshold for the solver"
    )
    use_gpu: bool = Field(
        True,
        description="Whether to use GPU acceleration if available"
    )

class StrategyNode(BaseModel):
    """Node in the game tree strategy"""
    fold: float = Field(0.0, description="Probability of folding")
    call: float = Field(0.0, description="Probability of calling")
    raise_: float = Field(0.0, alias="raise", description="Probability of raising")

class GTOSolution(BaseModel):
    """GTO solution output"""
    ip_strategy: Dict[str, StrategyNode] = Field(
        ...,
        description="Strategy for in-position player, keyed by hand"
    )
    oop_strategy: Dict[str, StrategyNode] = Field(
        ...,
        description="Strategy for out-of-position player, keyed by hand"
    )
    equity_ip: float = Field(
        ...,
        description="Equity of in-position player"
    )
    equity_oop: float = Field(
        ...,
        description="Equity of out-of-position player"
    )
    exploitability: float = Field(
        ...,
        description="Exploitability of the solution in big blinds per game"
    )
    iterations: int = Field(
        ...,
        description="Number of iterations performed"
    )
    converged: bool = Field(
        ...,
        description="Whether the solver converged to the desired accuracy"
    )
    solving_time: float = Field(
        ...,
        description="Time taken to solve in seconds"
    )

class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str = Field(..., description="Error message")

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    gpu_available: bool = Field(..., description="Whether GPU acceleration is available")
    gpu_in_use: bool = Field(..., description="Whether GPU acceleration is being used")
