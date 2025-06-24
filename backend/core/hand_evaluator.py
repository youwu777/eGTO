"""Hand evaluation logic for poker."""
from typing import Dict
from config.settings import settings


class HandEvaluator:
    """Simplified hand evaluator for CFR."""
    
    def __init__(self):
        self.hand_strengths = self._build_hand_strengths()
    
    def _build_hand_strengths(self) -> Dict[str, float]:
        """Build hand strength lookup table."""
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        strengths = {}
        
        # Pocket pairs
        for i, rank in enumerate(ranks):
            pair = f"{rank}{rank}"
            strengths[pair] = settings.hand_strength_base - (i * settings.hand_strength_decrement)
        
        # Suited combinations
        for i, rank1 in enumerate(ranks):
            for j, rank2 in enumerate(ranks[i+1:], i+1):
                suited = f"{rank1}{rank2}s"
                offsuit = f"{rank1}{rank2}o"
                
                # Base strength from high cards
                base_strength = (len(ranks) - i + len(ranks) - j) / (2 * len(ranks))
                
                # Suited gets bonus
                strengths[suited] = min(base_strength * settings.suited_bonus, 0.9)
                strengths[offsuit] = base_strength * settings.offsuit_penalty
        
        return strengths
    
    def get_hand_strength(self, hand: str) -> float:
        """Get normalized hand strength [0,1]."""
        return self.hand_strengths.get(hand, 0.5)
    
    def get_equity(self, hand1: str, hand2: str) -> float:
        """Get equity of hand1 vs hand2."""
        strength1 = self.get_hand_strength(hand1)
        strength2 = self.get_hand_strength(hand2)
        
        # Simplified equity calculation
        if strength1 == strength2:
            return 0.5
        
        diff = strength1 - strength2
        # Sigmoid-like function for equity
        equity = 0.5 + diff * 0.6
        return max(0.1, min(0.9, equity)) 