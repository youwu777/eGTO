"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings."""
    
    # API Settings
    app_name: str = "2-Player CFR GTO Solver"
    app_version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # CORS Settings
    allowed_origins: List[str] = ["*"]
    allowed_credentials: bool = True
    allowed_methods: List[str] = ["*"]
    allowed_headers: List[str] = ["*"]
    
    # CFR Training Settings
    default_iterations: int = 1000
    max_iterations: int = 10000
    min_iterations: int = 100
    
    # Game Settings
    default_pot_size: float = 100.0
    default_stack_size: float = 1000.0
    default_bet_size: float = 0.75  # 75% of pot
    max_bets_per_street: int = 4
    
    # Hand Evaluation Settings
    hand_strength_base: float = 0.85
    hand_strength_decrement: float = 0.05
    suited_bonus: float = 1.15
    offsuit_penalty: float = 0.9
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings() 