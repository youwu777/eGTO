"""Poker range handling and parsing."""
from typing import List, Dict


class PokerRange:
    """Complete poker range handling."""
    
    def __init__(self):
        self.hands = self._generate_all_hands()
        self.weights = {hand: 0.0 for hand in self.hands}
    
    def _generate_all_hands(self) -> List[str]:
        """Generate all 169 possible hole card combinations."""
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        hands = []
        
        # Pocket pairs
        for rank in ranks:
            hands.append(f"{rank}{rank}")
        
        # Suited and offsuit combinations
        for i, rank1 in enumerate(ranks):
            for j, rank2 in enumerate(ranks[i+1:], i+1):
                hands.append(f"{rank1}{rank2}s")
                hands.append(f"{rank1}{rank2}o")
        
        return hands
    
    def set_range_from_string(self, range_str: str) -> None:
        """Parse range string and set weights."""
        self.weights = {hand: 0.0 for hand in self.hands}
        
        if not range_str.strip():
            return
        
        # Split by commas and process each part
        parts = [part.strip() for part in range_str.split(',')]
        
        for part in parts:
            if ':' in part:
                # Handle weighted combos like "AA:0.5"
                hand, weight = part.split(':')
                weight = float(weight)
                if hand in self.weights:
                    self.weights[hand] = weight
            elif '-' in part and not part.endswith('s') and not part.endswith('o'):
                # Handle pair ranges like "AA-JJ"
                self._add_pair_range(part)
            elif '-' in part:
                # Handle other ranges like "AKs-ATs"
                self._add_combo_range(part)
            elif part.endswith('+'):
                # Handle plus notation like "AKo+"
                self._add_plus_range(part)
            else:
                # Single hand or hand type
                self._add_single_hand(part)
    
    def _add_pair_range(self, range_str: str) -> None:
        """Add pocket pair range like AA-JJ."""
        start, end = range_str.split('-')
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        
        start_idx = ranks.index(start[0])
        end_idx = ranks.index(end[0])
        
        for i in range(start_idx, end_idx + 1):
            pair = f"{ranks[i]}{ranks[i]}"
            if pair in self.weights:
                self.weights[pair] = 1.0
    
    def _add_combo_range(self, range_str: str) -> None:
        """Add combination range like AKs-ATs."""
        start, end = range_str.split('-')
        suited = start.endswith('s') or start.endswith('o')
        
        if not suited:
            return
        
        suit_type = start[-1]  # 's' or 'o'
        start_hand = start[:-1]
        end_hand = end[:-1]
        
        # Get the first rank and find range of second ranks
        first_rank = start_hand[0]
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        
        start_second = ranks.index(start_hand[1])
        end_second = ranks.index(end_hand[1])
        
        for i in range(start_second, end_second + 1):
            hand = f"{first_rank}{ranks[i]}{suit_type}"
            if hand in self.weights:
                self.weights[hand] = 1.0
    
    def _add_plus_range(self, range_str: str) -> None:
        """Add plus range like AKo+."""
        base_hand = range_str[:-1]  # Remove '+'
        if len(base_hand) < 2:
            return
        
        first_rank = base_hand[0]
        second_rank = base_hand[1]
        suit_type = base_hand[2:] if len(base_hand) > 2 else 'o'
        
        ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        second_idx = ranks.index(second_rank)
        
        # Add all hands with same first rank and second rank or better
        for i in range(0, second_idx + 1):
            if i != ranks.index(first_rank):  # Skip if same rank (would be pair)
                hand = f"{first_rank}{ranks[i]}{suit_type}"
                if hand in self.weights:
                    self.weights[hand] = 1.0
    
    def _add_single_hand(self, hand: str) -> None:
        """Add single hand to range."""
        if hand in self.weights:
            self.weights[hand] = 1.0
        elif len(hand) == 2:
            # Could be shorthand like AK (add both AKs and AKo)
            suited = f"{hand}s"
            offsuit = f"{hand}o"
            if suited in self.weights:
                self.weights[suited] = 1.0
            if offsuit in self.weights:
                self.weights[offsuit] = 1.0
    
    def get_weighted_hands(self) -> Dict[str, float]:
        """Get all hands with non-zero weights."""
        return {hand: weight for hand, weight in self.weights.items() if weight > 0}
    
    def get_total_combos(self) -> float:
        """Get total number of combinations in range."""
        return sum(self.weights.values()) 