"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    app_name: str = "2-Player CFR GTO Solver"
    app_version: str = "2.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Settings
    allowed_origins: List[str] = ["*"]
    allowed_credentials: bool = True
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    # GTO Solver Settings
    default_iterations: int = 100000  # Increased for convergence
    max_iterations: int = 1000000
    min_iterations: int = 10000
    convergence_threshold: float = 0.001  # Strategy convergence threshold
    
    # Game Settings
    default_pot_size: float = 100.0
    default_stack_size: float = 1000.0
    bet_sizes: List[float] = [0.33, 0.5, 0.75, 1.0, 1.5, 2.0]  # Multiple bet sizes
    max_bets_per_street: int = 4
    max_streets: int = 4  # preflop, flop, turn, river
    
    # Hand Evaluation Settings
    hand_strength_base: float = 0.85
    hand_strength_decrement: float = 0.05
    suited_bonus: float = 1.15
    offsuit_penalty: float = 0.9
    
    # Monte Carlo Settings
    mc_simulations: int = 10000  # For equity calculations
    board_samples: int = 1000    # For board texture analysis
    
    # Memory and Performance
    max_nodes_in_memory: int = 1000000
    save_strategies: bool = True
    strategy_cache_size: int = 10000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 