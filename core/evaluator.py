import numpy as np
from numba import jit, cuda
import cupy as cp
from typing import List, Dict, Tuple, Set, Optional

class HandEvaluator:
    def __init__(self):
        # Initialize card mappings and lookup tables
        self.rank_to_prime = {
            '2': 2, '3': 3, '4': 5, '5': 7, '6': 11, '7': 13, '8': 17,
            '9': 19, 'T': 23, 'J': 29, 'Q': 31, 'K': 37, 'A': 41
        }
        self.suit_to_bits = {'c': 1, 'd': 2, 'h': 4, 's': 8}
        self.hand_rank_values = {
            'high_card': 0,
            'pair': 1,
            'two_pair': 2,
            'three_of_a_kind': 3,
            'straight': 4,
            'flush': 5,
            'full_house': 6,
            'four_of_a_kind': 7,
            'straight_flush': 8,
            'royal_flush': 9
        }
    
    def evaluate_hand(self, cards: List[str]) -> int:
        """Evaluate the strength of a poker hand (up to 7 cards)"""
        if len(cards) < 2 or len(cards) > 7:
            raise ValueError("Hand must contain between 2 and 7 cards")
            
        ranks = []
        suits = []
        for card in cards:
            rank = card[0].upper()
            suit = card[1].lower()
            if rank not in self.rank_to_prime or suit not in self.suit_to_bits:
                raise ValueError(f"Invalid card: {card}")
            ranks.append(rank)
            suits.append(suit)
        
        flush_suit = self._has_flush(suits)
        straight_high = self._has_straight(ranks)
        rank_counts = self._get_rank_counts(ranks)
        
        if flush_suit and straight_high:
            if straight_high == 14:  # Royal flush
                return self._make_hand_value(self.hand_rank_values['royal_flush'], 0)
            return self._make_hand_value(self.hand_rank_values['straight_flush'], straight_high)
        
        if 4 in rank_counts.values():
            quad_rank = [r for r, cnt in rank_counts.items() if cnt == 4][0]
            kicker = max(r for r in rank_counts if r != quad_rank)
            return self._make_hand_value(self.hand_rank_values['four_of_a_kind'], 
                                      (quad_rank << 8) | kicker)
        
        trips = [r for r, cnt in rank_counts.items() if cnt >= 3]
        if trips:
            trips_rank = max(trips)
            pairs = [r for r, cnt in rank_counts.items() if cnt >= 2 and r != trips_rank]
            if pairs:
                pair_rank = max(pairs)
                return self._make_hand_value(self.hand_rank_values['full_house'],
                                          (trips_rank << 8) | pair_rank)
        
        if flush_suit:
            flush_cards = [r for r, s in zip(ranks, suits) if s == flush_suit]
            flush_ranks = sorted([self.rank_to_prime[r] for r in flush_cards], reverse=True)[:5]
            flush_value = 0
            for i, r in enumerate(flush_ranks):
                flush_value |= (r << (16 - i * 4))
            return self._make_hand_value(self.hand_rank_values['flush'], flush_value)
        
        if straight_high:
            return self._make_hand_value(self.hand_rank_values['straight'], straight_high)
        
        if trips:
            trips_rank = max(trips)
            kickers = sorted([r for r in rank_counts if r != trips_rank], reverse=True)[:2]
            kicker_value = (kickers[0] << 4) | kickers[1] if len(kickers) > 1 else kickers[0] << 4
            return self._make_hand_value(self.hand_rank_values['three_of_a_kind'],
                                      (trips_rank << 8) | kicker_value)
        
        pairs = [r for r, cnt in rank_counts.items() if cnt == 2]
        if len(pairs) >= 2:
            pairs_sorted = sorted(pairs, reverse=True)[:2]
            kicker = max(r for r in rank_counts if r not in pairs_sorted)
            return self._make_hand_value(self.hand_rank_values['two_pair'],
                                      (pairs_sorted[0] << 12) | (pairs_sorted[1] << 8) | kicker)
        
        if pairs:
            pair_rank = max(pairs)
            kickers = sorted([r for r in rank_counts if r != pair_rank], reverse=True)[:3]
            kicker_value = (kickers[0] << 8) | (kickers[1] << 4) | kickers[2] if len(kickers) > 2 else 0
            return self._make_hand_value(self.hand_rank_values['pair'],
                                      (pair_rank << 16) | kicker_value)
        
        high_cards = sorted(ranks, key=lambda x: -self.rank_to_prime[x])[:5]
        high_value = 0
        for i, r in enumerate(high_cards):
            high_value |= (self.rank_to_prime[r] << (16 - i * 4))
        return self._make_hand_value(self.hand_rank_values['high_card'], high_value)
    
    def _has_flush(self, suits: List[str]) -> Optional[str]:
        """Check if there's a flush and return the suit if so"""
        suit_counts = {}
        for suit in suits:
            suit_counts[suit] = suit_counts.get(suit, 0) + 1
            if suit_counts[suit] >= 5:
                return suit
        return None
    
    def _has_straight(self, ranks: List[str]) -> int:
        """Check for a straight and return the high card rank if found"""
        rank_set = set(self.rank_to_prime[r] for r in ranks)
        if 14 in rank_set:  # Add low ace for wheel straight (A-2-3-4-5)
            rank_set.add(1)
        
        for high in range(14, 4, -1):
            if all(r in rank_set for r in range(high, high-5, -1)):
                return high
        return 0
    
    def _get_rank_counts(self, ranks: List[str]) -> Dict[int, int]:
        """Count occurrences of each rank"""
        rank_counts = {}
        for r in ranks:
            rank = self.rank_to_prime[r]
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        return rank_counts
    
    def _make_hand_value(self, hand_type: int, value: int) -> int:
        """Combine hand type and value into a single integer for comparison"""
        return (hand_type << 20) | value

class Range:
    def __init__(self, range_str: str = None):
        self.hands: Dict[str, float] = {}
        if range_str:
            self.parse_range(range_str)
    
    def parse_range(self, range_str: str) -> None:
        """Parse a range string into individual hands with weights"""
        # This is a simplified version - in practice, you'd want to support
        # all common range notation (e.g., "AKs, TT+, 98s+")
        hands = range_str.split(',')
        for hand in hands:
            hand = hand.strip()
            if not hand:
                continue
            
            # Simple pair (e.g., "AA")
            if len(hand) == 2 and hand[0] == hand[1].upper():
                rank = hand[0].upper()
                for s1 in ['c', 'd', 'h', 's']:
                    for s2 in [s for s in ['c', 'd', 'h', 's'] if s != s1]:
                        self.hands[f"{rank}{s1}{rank}{s2}"] = 1.0
            # Suited (e.g., "AKs")
            elif len(hand) == 3 and hand[2] == 's':
                r1, r2 = hand[0].upper(), hand[1].upper()
                for s in ['c', 'd', 'h', 's']:
                    self.hands[f"{r1}{s}{r2}{s}"] = 1.0
            # Offsuit (e.g., "AKo")
            elif len(hand) == 3 and hand[2] == 'o':
                r1, r2 = hand[0].upper(), hand[1].upper()
                for s1 in ['c', 'd', 'h', 's']:
                    for s2 in [s for s in ['c', 'd', 'h', 's'] if s != s1]:
                        self.hands[f"{r1}{s1}{r2}{s2}"] = 1.0
    
    def add_hand(self, hand: str, weight: float = 1.0) -> None:
        """Add a specific hand to the range with optional weight"""
        self.hands[hand] = weight
    
    def remove_hand(self, hand: str) -> None:
        """Remove a hand from the range"""
        if hand in self.hands:
            del self.hands[hand]
    
    def get_hands(self) -> Dict[str, float]:
        """Get all hands in the range with their weights"""
        return self.hands
    
    def normalize_weights(self) -> None:
        """Normalize hand weights to sum to 1.0"""
        total = sum(self.hands.values())
        if total > 0:
            self.hands = {h: w/total for h, w in self.hands.items()}

class GameState:
    def __init__(self, effective_stack: float = 100.0, pot: float = 1.0):
        self.effective_stack = effective_stack
        self.pot = pot
        self.current_street = "preflop"  # preflop, flop, turn, river
        self.board: List[str] = []
        self.pot_odds = 0.0
        self.to_call = 0.0
    
    def update_street(self, street: str) -> None:
        """Update the current street"""
        valid_streets = ["preflop", "flop", "turn", "river", "showdown"]
        if street not in valid_streets:
            raise ValueError(f"Invalid street: {street}. Must be one of {valid_streets}")
        self.current_street = street
    
    def add_to_board(self, cards: List[str]) -> None:
        """Add cards to the board"""
        for card in cards:
            if len(card) != 2:
                raise ValueError(f"Invalid card format: {card}")
            self.board.append(card)
        
        # Update street based on number of board cards
        if len(self.board) == 3:
            self.update_street("flop")
        elif len(self.board) == 4:
            self.update_street("turn")
        elif len(self.board) == 5:
            self.update_street("river")
    
    def calculate_pot_odds(self, bet_size: float) -> float:
        """Calculate pot odds for a given bet size"""
        return bet_size / (self.pot + bet_size + self.to_call)
    
    def update_pot(self, amount: float) -> None:
        """Update the pot size"""
        self.pot += amount
