"""Game-related data models."""
from dataclasses import dataclass
from typing import List, Optional, Dict
from .enums import ActionType, Street, BetSize, BoardTexture


@dataclass
class Action:
    """Represents a poker action."""
    type: ActionType
    size: float = 0.0
    bet_size_type: Optional[BetSize] = None
    
    def __str__(self) -> str:
        """String representation of action."""
        if self.size > 0:
            return f"{self.type.value}_{self.size:.1f}"
        return self.type.value


@dataclass
class Board:
    """Represents the community board."""
    cards: List[str] = None  # e.g., ["Ah", "Ks", "Qd"]
    texture: BoardTexture = None
    
    def __post_init__(self):
        if self.cards is None:
            self.cards = []
    
    def add_card(self, card: str):
        """Add a card to the board."""
        self.cards.append(card)
        self._update_texture()
    
    def _update_texture(self):
        """Update board texture classification."""
        if len(self.cards) < 3:
            return
        
        # Basic texture analysis
        ranks = [card[0] for card in self.cards]
        suits = [card[1] for card in self.cards]
        
        if len(set(ranks)) < len(ranks):
            self.texture = BoardTexture.PAIRED
        elif len(set(suits)) == 1:
            self.texture = BoardTexture.SUITED
        elif self._is_connected(ranks):
            self.texture = BoardTexture.CONNECTED
        elif self._has_high_cards(ranks):
            self.texture = BoardTexture.HIGH_CARDS
        else:
            self.texture = BoardTexture.DRY
    
    def _is_connected(self, ranks: List[str]) -> bool:
        """Check if board is connected."""
        rank_order = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        rank_indices = [rank_order.index(r) for r in ranks]
        rank_indices.sort()
        
        for i in range(len(rank_indices) - 1):
            if rank_indices[i+1] - rank_indices[i] <= 2:
                return True
        return False
    
    def _has_high_cards(self, ranks: List[str]) -> bool:
        """Check if board has high cards."""
        high_ranks = ['A', 'K', 'Q', 'J']
        return any(r in high_ranks for r in ranks)


@dataclass
class GameConfig:
    """Game configuration with user-defined parameters."""
    bet_sizes: List[float] = None  # Custom bet sizes as fractions of pot
    max_bets_per_street: Dict[str, int] = None  # Max bets per street
    allow_all_in: bool = True
    min_raise_size: float = 0.5  # Minimum raise as fraction of pot
    
    def __post_init__(self):
        if self.bet_sizes is None:
            self.bet_sizes = [0.33, 0.5, 0.75, 1.0, 1.5, 2.0]
        if self.max_bets_per_street is None:
            self.max_bets_per_street = {
                "preflop": 4,
                "flop": 3,
                "turn": 2,
                "river": 1
            }
    
    def get_max_bets_for_street(self, street: Street) -> int:
        """Get max bets for specific street."""
        return self.max_bets_per_street.get(street.value, 1)
    
    def get_available_bet_sizes(self, pot_size: float, effective_stack: float, 
                               current_bet: float = 0) -> List[float]:
        """Get available bet sizes for current situation."""
        available_sizes = []
        
        for bet_ratio in self.bet_sizes:
            bet_size = pot_size * bet_ratio
            if bet_size <= effective_stack and bet_size > current_bet:
                available_sizes.append(bet_size)
        
        # Add all-in if allowed and not already included
        if self.allow_all_in and effective_stack > current_bet:
            if effective_stack not in available_sizes:
                available_sizes.append(effective_stack)
        
        return sorted(available_sizes)


@dataclass
class GameState:
    """Comprehensive game state for full postflop game tree."""
    pot: float
    oop_invested: float
    ip_invested: float
    oop_stack: float
    ip_stack: float
    to_act: str  # Position enum value
    history: List[Action]
    street: Street
    board: Board
    max_bets: int
    bet_count: int = 0
    last_bet_size: float = 0.0
    min_raise: float = 0.0
    game_config: GameConfig = None
    
    def __post_init__(self):
        if self.board is None:
            self.board = Board()
        if self.game_config is None:
            self.game_config = GameConfig()
    
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
        
        # Terminal if max bets reached for current street
        max_bets_for_street = self.game_config.get_max_bets_for_street(self.street)
        if self.bet_count >= max_bets_for_street:
            return True
        
        # Terminal if all-in
        if self.oop_stack <= 0 or self.ip_stack <= 0:
            return True
            
        return False
    
    def get_street_number(self) -> int:
        """Get street as number (0=preflop, 1=flop, 2=turn, 3=river)."""
        street_map = {
            Street.PREFLOP: 0,
            Street.FLOP: 1,
            Street.TURN: 2,
            Street.RIVER: 3
        }
        return street_map.get(self.street, 0)
    
    def get_effective_stack(self) -> float:
        """Get the smaller of the two stacks."""
        return min(self.oop_stack, self.ip_stack)
    
    def get_pot_odds(self) -> float:
        """Calculate pot odds for the acting player."""
        current_bet = max(self.oop_invested, self.ip_invested)
        acting_invested = (self.oop_invested if self.to_act == "oop" 
                          else self.ip_invested)
        bet_to_call = current_bet - acting_invested
        
        if bet_to_call <= 0:
            return float('inf')
        
        return self.pot / bet_to_call
    
    def get_available_bet_sizes(self) -> List[float]:
        """Get available bet sizes for current situation."""
        current_bet = max(self.oop_invested, self.ip_invested)
        effective_stack = self.get_effective_stack()
        
        return self.game_config.get_available_bet_sizes(
            self.pot, effective_stack, current_bet
        )


@dataclass
class HandStrength:
    """Detailed hand strength information."""
    absolute_strength: float  # 0-1 scale
    relative_strength: float  # vs opponent range
    equity_vs_range: float    # equity vs opponent range
    nut_potential: float      # potential to make nuts
    board_interaction: float  # how well hand interacts with board
    blockers: List[str]       # cards that block opponent's strong hands 