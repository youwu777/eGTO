"""Game-related data models."""
from dataclasses import dataclass
from typing import List
from .enums import ActionType


@dataclass
class Action:
    """Represents a poker action."""
    type: ActionType
    size: float = 0.0
    
    def __str__(self) -> str:
        """String representation of action."""
        if self.size > 0:
            return f"{self.type.value}_{self.size:.1f}"
        return self.type.value


@dataclass
class GameState:
    """Simplified 2-player game state."""
    pot: float
    oop_invested: float
    ip_invested: float
    oop_stack: float
    ip_stack: float
    to_act: str  # Position enum value
    history: List[Action]
    street: int  # 0=preflop, 1=flop, 2=turn, 3=river
    max_bets: int
    bet_count: int = 0
    
    def is_terminal(self) -> bool:
        """Check if game state is terminal."""
        # Terminal if someone folded
        if self.history and self.history[-1].type == ActionType.FOLD:
            return True
        
        # Terminal if both players checked (and no bets this street)
        if len(self.history) >= 2 and self.bet_count == 0:
            if all(action.type == ActionType.CHECK for action in self.history[-2:]):
                return True
        
        # Terminal if call after bet
        if len(self.history) >= 2:
            if (self.history[-2].type == ActionType.BET and 
                self.history[-1].type == ActionType.CALL):
                return True
        
        # Terminal if max bets reached
        if self.bet_count >= self.max_bets:
            return True
            
        return False 