"""API request and response models."""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from .enums import Street, BetSize


class SolverRequest(BaseModel):
    """Request model for comprehensive solver endpoint."""
    oop_range: str = Field(..., description="OOP range string (e.g., 'AA-77,AKs-ATs,AKo-AJo')")
    ip_range: str = Field(..., description="IP range string")
    starting_stack: float = Field(..., gt=0, description="Starting stack size")
    pot_size: float = Field(..., gt=0, description="Initial pot size")
    max_bets: int = Field(..., ge=1, le=4, description="Maximum number of bets/raises")
    iterations: Optional[int] = Field(100000, ge=1000, le=1000000, description="Training iterations")
    board_cards: Optional[List[str]] = Field([], description="Board cards (e.g., ['Ah', 'Ks', 'Qd'])")
    street: Optional[Street] = Field(Street.PREFLOP, description="Current street")
    convergence_threshold: Optional[float] = Field(0.001, gt=0, le=0.1, description="Convergence threshold")
    
    # User-configurable bet sizes and max bets
    bet_sizes: Optional[List[float]] = Field(
        [0.33, 0.5, 0.75, 1.0, 1.5, 2.0], 
        description="Custom bet sizes as fractions of pot (e.g., [0.5, 1.0, 2.0])"
    )
    max_bets_per_street: Optional[Dict[str, int]] = Field(
        {"preflop": 4, "flop": 3, "turn": 2, "river": 1},
        description="Max bets allowed per street"
    )
    allow_all_in: Optional[bool] = Field(True, description="Allow all-in as a bet option")
    min_raise_size: Optional[float] = Field(0.5, description="Minimum raise size as fraction of pot")


class HandAnalysis(BaseModel):
    """Detailed hand analysis."""
    strategy: Dict[str, float]
    absolute_strength: Optional[float] = None
    relative_strength: Optional[float] = None
    equity_vs_range: Optional[float] = None
    nut_potential: Optional[float] = None
    board_interaction: Optional[float] = None
    blockers: Optional[List[str]] = None
    board_texture: Optional[str] = None
    pot_odds: Optional[float] = None


class ConvergenceData(BaseModel):
    """Convergence tracking data."""
    iteration: int
    convergence: float
    nodes_count: int


class SolverResponse(BaseModel):
    """Response model for comprehensive solver endpoint."""
    oop_strategy: Dict[str, HandAnalysis]
    ip_strategy: Dict[str, HandAnalysis]
    training_iterations: int
    computation_time: float
    nodes_count: int
    convergence_history: List[ConvergenceData]
    final_convergence: float
    board_texture: Optional[str] = None
    bet_sizes_used: List[float]
    max_bets_per_street: Dict[str, int]


class PostflopRequest(BaseModel):
    """Request model for postflop analysis."""
    hand: str = Field(..., description="Player's hand (e.g., 'AA', 'AKs')")
    position: str = Field(..., description="Player position ('oop' or 'ip')")
    board_cards: List[str] = Field(..., description="Board cards")
    opponent_range: str = Field(..., description="Opponent's range")
    pot_size: float = Field(..., gt=0, description="Current pot size")
    stack_size: float = Field(..., gt=0, description="Stack size")
    action_history: Optional[List[str]] = Field([], description="Action history")
    
    # User-configurable parameters for postflop analysis
    bet_sizes: Optional[List[float]] = Field(
        [0.33, 0.5, 0.75, 1.0, 1.5, 2.0],
        description="Available bet sizes for this spot"
    )
    max_bets_remaining: Optional[int] = Field(3, description="Max bets remaining in this street")
    allow_all_in: Optional[bool] = Field(True, description="Allow all-in as option")
    min_raise_size: Optional[float] = Field(0.5, description="Minimum raise size")


class PostflopResponse(BaseModel):
    """Response model for postflop analysis."""
    strategy: Dict[str, float]
    hand_strength: HandAnalysis
    board_texture: str
    pot_odds: float
    position: str
    equity_vs_range: float
    recommended_action: str
    confidence: float
    available_actions: List[str]
    bet_sizes_available: List[float]


class GameConfigRequest(BaseModel):
    """Request model for game configuration validation."""
    bet_sizes: List[float] = Field(..., description="Bet sizes to validate")
    max_bets_per_street: Dict[str, int] = Field(..., description="Max bets per street")
    starting_stack: float = Field(..., gt=0, description="Starting stack")
    pot_size: float = Field(..., gt=0, description="Pot size")


class GameConfigResponse(BaseModel):
    """Response model for game configuration validation."""
    is_valid: bool
    warnings: List[str]
    estimated_nodes: int
    estimated_training_time: float
    recommended_iterations: int 