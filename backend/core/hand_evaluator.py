"""Comprehensive hand evaluation logic for GTO poker."""
import random
import itertools
from typing import Dict, List, Tuple, Set
from models.enums import BoardTexture
from models.game_models import HandStrength, Board
from config.settings import settings


class HandEvaluator:
    """Comprehensive hand evaluator with Monte Carlo equity calculations."""
    
    def __init__(self):
        self.hand_strengths = self._build_hand_strengths()
        self.rank_order = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
        self.suits = ['h', 'd', 'c', 's']
    
    def _build_hand_strengths(self) -> Dict[str, float]:
        """Build comprehensive hand strength lookup table."""
        strengths = {}
        
        # Pocket pairs
        for i, rank in enumerate(self.rank_order):
            pair = f"{rank}{rank}"
            strengths[pair] = settings.hand_strength_base - (i * settings.hand_strength_decrement)
        
        # Suited and offsuit combinations
        for i, rank1 in enumerate(self.rank_order):
            for j, rank2 in enumerate(self.rank_order[i+1:], i+1):
                suited = f"{rank1}{rank2}s"
                offsuit = f"{rank1}{rank2}o"
                
                # Base strength from high cards
                base_strength = (len(self.rank_order) - i + len(self.rank_order) - j) / (2 * len(self.rank_order))
                
                # Suited gets bonus
                strengths[suited] = min(base_strength * settings.suited_bonus, 0.9)
                strengths[offsuit] = base_strength * settings.offsuit_penalty
        
        return strengths
    
    def get_hand_strength(self, hand: str) -> float:
        """Get normalized hand strength [0,1]."""
        return self.hand_strengths.get(hand, 0.5)
    
    def calculate_equity_monte_carlo(self, hand1: str, hand2: str, board: Board = None) -> float:
        """Calculate equity using Monte Carlo simulation."""
        if board is None:
            board = Board()
        
        wins = 0
        total_sims = settings.mc_simulations
        
        # Extract cards from hands and board
        hand1_cards = self._parse_hand(hand1)
        hand2_cards = self._parse_hand(hand2)
        board_cards = board.cards.copy()
        
        # Remove used cards from deck
        used_cards = set(hand1_cards + hand2_cards + board_cards)
        deck = self._create_deck(used_cards)
        
        for _ in range(total_sims):
            # Complete the board randomly
            remaining_cards = deck.copy()
            random.shuffle(remaining_cards)
            
            # Complete to 5 cards
            while len(board_cards) < 5:
                board_cards.append(remaining_cards.pop())
            
            # Evaluate hands
            hand1_rank = self._evaluate_hand(hand1_cards + board_cards)
            hand2_rank = self._evaluate_hand(hand2_cards + board_cards)
            
            if hand1_rank < hand2_rank:  # Lower rank = better hand
                wins += 1
            elif hand1_rank == hand2_rank:
                wins += 0.5  # Split pot
        
        return wins / total_sims
    
    def calculate_equity_vs_range(self, hand: str, opponent_range: Dict[str, float], 
                                 board: Board = None) -> float:
        """Calculate equity vs opponent range."""
        if board is None:
            board = Board()
        
        total_equity = 0.0
        total_weight = 0.0
        
        for opponent_hand, weight in opponent_range.items():
            if weight <= 0:
                continue
            
            # Skip if hands conflict
            if self._hands_conflict(hand, opponent_hand):
                continue
            
            equity = self.calculate_equity_monte_carlo(hand, opponent_hand, board)
            total_equity += equity * weight
            total_weight += weight
        
        return total_equity / total_weight if total_weight > 0 else 0.5
    
    def get_hand_strength_detailed(self, hand: str, board: Board, 
                                  opponent_range: Dict[str, float]) -> HandStrength:
        """Get comprehensive hand strength analysis."""
        # Absolute strength
        absolute_strength = self.get_hand_strength(hand)
        
        # Equity vs opponent range
        equity_vs_range = self.calculate_equity_vs_range(hand, opponent_range, board)
        
        # Relative strength (how strong vs opponent's range)
        relative_strength = equity_vs_range
        
        # Nut potential (simplified)
        nut_potential = self._calculate_nut_potential(hand, board)
        
        # Board interaction
        board_interaction = self._calculate_board_interaction(hand, board)
        
        # Blockers
        blockers = self._identify_blockers(hand, opponent_range)
        
        return HandStrength(
            absolute_strength=absolute_strength,
            relative_strength=relative_strength,
            equity_vs_range=equity_vs_range,
            nut_potential=nut_potential,
            board_interaction=board_interaction,
            blockers=blockers
        )
    
    def _parse_hand(self, hand: str) -> List[str]:
        """Parse hand string to card list."""
        if len(hand) == 2:  # Pocket pair
            rank = hand[0]
            return [f"{rank}h", f"{rank}d"]  # Simplified - just use two suits
        elif len(hand) >= 3:
            rank1, rank2 = hand[0], hand[1]
            if hand.endswith('s'):  # Suited
                return [f"{rank1}h", f"{rank2}h"]
            else:  # Offsuit
                return [f"{rank1}h", f"{rank2}d"]
        return []
    
    def _create_deck(self, used_cards: Set[str]) -> List[str]:
        """Create deck excluding used cards."""
        deck = []
        for rank in self.rank_order:
            for suit in self.suits:
                card = f"{rank}{suit}"
                if card not in used_cards:
                    deck.append(card)
        return deck
    
    def _evaluate_hand(self, cards: List[str]) -> int:
        """Evaluate hand strength (lower = better)."""
        # Simplified hand evaluation - in production would use proper poker hand evaluator
        ranks = [card[0] for card in cards]
        suits = [card[1] for card in cards]
        
        # Count rank frequencies
        rank_counts = {}
        for rank in ranks:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        
        # Hand rankings (simplified)
        if len(set(suits)) == 1 and len(cards) >= 5:  # Flush
            return 5
        elif 4 in rank_counts.values():  # Four of a kind
            return 7
        elif 3 in rank_counts.values() and 2 in rank_counts.values():  # Full house
            return 6
        elif 3 in rank_counts.values():  # Three of a kind
            return 3
        elif list(rank_counts.values()).count(2) == 2:  # Two pair
            return 2
        elif 2 in rank_counts.values():  # One pair
            return 1
        else:  # High card
            return 0
    
    def _hands_conflict(self, hand1: str, hand2: str) -> bool:
        """Check if two hands share cards."""
        # Simplified - just check if hands are identical
        return hand1 == hand2
    
    def _calculate_nut_potential(self, hand: str, board: Board) -> float:
        """Calculate nut potential of hand on given board."""
        # Simplified calculation
        if len(board.cards) == 0:  # Preflop
            if hand in ['AA', 'KK', 'QQ']:
                return 0.9
            elif hand.endswith('s') and hand[0] in ['A', 'K', 'Q']:
                return 0.7
            else:
                return 0.5
        else:
            # Postflop - would need more sophisticated analysis
            return 0.6
    
    def _calculate_board_interaction(self, hand: str, board: Board) -> float:
        """Calculate how well hand interacts with board."""
        if len(board.cards) == 0:
            return 0.5
        
        # Simplified board interaction
        hand_cards = self._parse_hand(hand)
        board_ranks = [card[0] for card in board.cards]
        
        # Check for pairs, draws, etc.
        interaction_score = 0.5
        
        # Pair with board
        for card in hand_cards:
            if card[0] in board_ranks:
                interaction_score += 0.2
        
        # Flush draw potential
        hand_suits = [card[1] for card in hand_cards]
        board_suits = [card[1] for card in board.cards]
        if len(set(hand_suits + board_suits)) <= 2:
            interaction_score += 0.1
        
        return min(interaction_score, 1.0)
    
    def _identify_blockers(self, hand: str, opponent_range: Dict[str, float]) -> List[str]:
        """Identify cards that block opponent's strong hands."""
        blockers = []
        hand_cards = self._parse_hand(hand)
        
        # Check which strong hands are blocked
        strong_hands = ['AA', 'KK', 'QQ', 'JJ', 'AKs', 'AKo', 'AQs', 'AQo']
        
        for strong_hand in strong_hands:
            strong_cards = self._parse_hand(strong_hand)
            if any(card in hand_cards for card in strong_cards):
                blockers.append(strong_hand)
        
        return blockers
    
    def get_equity(self, hand1: str, hand2: str) -> float:
        """Get equity of hand1 vs hand2 (legacy method)."""
        return self.calculate_equity_monte_carlo(hand1, hand2) 