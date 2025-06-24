"""Validation utilities for the poker application."""
from typing import List
from models.enums import Position, ActionType


def validate_range_string(range_str: str) -> bool:
    """Validate poker range string format."""
    if not range_str or not range_str.strip():
        return False
    
    # Basic validation - could be expanded
    valid_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,+-:so')
    return all(c.upper() in valid_chars for c in range_str)


def validate_game_parameters(pot_size: float, stack_size: float, max_bets: int) -> List[str]:
    """Validate game parameters and return list of errors."""
    errors = []
    
    if pot_size <= 0:
        errors.append("Pot size must be positive")
    
    if stack_size <= 0:
        errors.append("Stack size must be positive")
    
    if max_bets < 1 or max_bets > 4:
        errors.append("Max bets must be between 1 and 4")
    
    return errors 