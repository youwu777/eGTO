"""2-Player CFR Solver for OOP vs IP."""
import random
from typing import Dict, List, Tuple
from models.enums import Position, ActionType
from models.game_models import GameState, Action
from core.hand_evaluator import HandEvaluator
from core.poker_range import PokerRange
from .cfr_node import CFRNode
from config.settings import settings


class CFRSolver:
    """2-Player CFR Solver for OOP vs IP."""
    
    def __init__(self):
        self.nodes = {}
        self.hand_evaluator = HandEvaluator()
        self.iterations = 0
        
    def get_info_set(self, hand: str, history: List[Action], position: Position) -> str:
        """Create information set string."""
        history_str = ''.join([str(action) for action in history])
        return f"{position.value}:{hand}:{history_str}"
    
    def get_available_actions(self, game_state: GameState) -> List[Action]:
        """Get available actions for current game state."""
        actions = []
        
        # Determine if there's a bet to face
        current_bet = max(game_state.oop_invested, game_state.ip_invested)
        acting_invested = (game_state.oop_invested if game_state.to_act == Position.OOP 
                          else game_state.ip_invested)
        
        bet_to_call = current_bet - acting_invested
        
        if bet_to_call > 0:
            # Facing a bet - can fold or call
            actions.append(Action(ActionType.FOLD))
            actions.append(Action(ActionType.CALL, bet_to_call))
            
            # Can raise if under max bets
            if game_state.bet_count < game_state.max_bets:
                # Fixed bet size for simplicity
                bet_size = game_state.pot * settings.default_bet_size
                actions.append(Action(ActionType.BET, bet_size))
        else:
            # No bet to face - can check or bet
            actions.append(Action(ActionType.CHECK))
            
            # Can bet if under max bets
            if game_state.bet_count < game_state.max_bets:
                bet_size = game_state.pot * settings.default_bet_size
                actions.append(Action(ActionType.BET, bet_size))
        
        return actions
    
    def apply_action(self, game_state: GameState, action: Action) -> GameState:
        """Apply action and return new game state."""
        new_pot = game_state.pot
        new_oop_invested = game_state.oop_invested
        new_ip_invested = game_state.ip_invested
        new_oop_stack = game_state.oop_stack
        new_ip_stack = game_state.ip_stack
        new_bet_count = game_state.bet_count
        
        # Apply action based on who's acting
        if game_state.to_act == Position.OOP:
            if action.type in [ActionType.CALL, ActionType.BET]:
                new_oop_invested += action.size
                new_oop_stack -= action.size
                new_pot += action.size
                if action.type == ActionType.BET:
                    new_bet_count += 1
            new_to_act = Position.IP
        else:  # IP acting
            if action.type in [ActionType.CALL, ActionType.BET]:
                new_ip_invested += action.size
                new_ip_stack -= action.size
                new_pot += action.size
                if action.type == ActionType.BET:
                    new_bet_count += 1
            new_to_act = Position.OOP
        
        return GameState(
            pot=new_pot,
            oop_invested=new_oop_invested,
            ip_invested=new_ip_invested,
            oop_stack=new_oop_stack,
            ip_stack=new_ip_stack,
            to_act=new_to_act,
            history=game_state.history + [action],
            street=game_state.street,
            max_bets=game_state.max_bets,
            bet_count=new_bet_count
        )
    
    def get_payoff(self, game_state: GameState, oop_hand: str, ip_hand: str) -> Tuple[float, float]:
        """Calculate payoffs at terminal node."""
        if game_state.history and game_state.history[-1].type == ActionType.FOLD:
            # Someone folded
            if game_state.to_act == Position.IP:
                # OOP folded (IP was about to act)
                return (-game_state.oop_invested, game_state.pot - game_state.ip_invested)
            else:
                # IP folded (OOP was about to act)
                return (game_state.pot - game_state.oop_invested, -game_state.ip_invested)
        else:
            # Showdown - compare hands
            oop_equity = self.hand_evaluator.get_equity(oop_hand, ip_hand)
            ip_equity = 1.0 - oop_equity
            
            oop_payoff = oop_equity * game_state.pot - game_state.oop_invested
            ip_payoff = ip_equity * game_state.pot - game_state.ip_invested
            
            return (oop_payoff, ip_payoff)
    
    def cfr(self, game_state: GameState, oop_hand: str, ip_hand: str, 
            oop_reach: float, ip_reach: float) -> Tuple[float, float]:
        """Main CFR algorithm."""
        
        if game_state.is_terminal():
            return self.get_payoff(game_state, oop_hand, ip_hand)
        
        # Get acting player and create info set
        acting_player = Position(game_state.to_act)
        hand = oop_hand if acting_player == Position.OOP else ip_hand
        info_set = self.get_info_set(hand, game_state.history, acting_player)
        
        # Get available actions
        actions = self.get_available_actions(game_state)
        action_strs = [str(action) for action in actions]
        
        # Initialize node if not exists
        if info_set not in self.nodes:
            self.nodes[info_set] = CFRNode(info_set, action_strs)
        
        node = self.nodes[info_set]
        
        # Get current strategy
        realization_weight = oop_reach if acting_player == Position.OOP else ip_reach
        strategy = node.get_strategy(realization_weight)
        
        # Initialize utilities
        action_utilities = {}
        oop_utility = 0.0
        ip_utility = 0.0
        
        # Recursively compute utilities for each action
        for i, action in enumerate(actions):
            action_str = action_strs[i]
            new_game_state = self.apply_action(game_state, action)
            
            if acting_player == Position.OOP:
                new_oop_reach = oop_reach * strategy[action_str]
                new_ip_reach = ip_reach
            else:
                new_oop_reach = oop_reach
                new_ip_reach = ip_reach * strategy[action_str]
            
            action_oop_utility, action_ip_utility = self.cfr(
                new_game_state, oop_hand, ip_hand, new_oop_reach, new_ip_reach
            )
            
            action_utilities[action_str] = (action_oop_utility, action_ip_utility)
            
            # Weight by strategy probability
            oop_utility += strategy[action_str] * action_oop_utility
            ip_utility += strategy[action_str] * action_ip_utility
        
        # Update regrets for acting player
        for action_str in action_strs:
            action_utility = action_utilities[action_str]
            
            if acting_player == Position.OOP:
                regret = action_utility[0] - oop_utility
                node.regret_sum[action_str] += ip_reach * regret  # Opponent reach
            else:
                regret = action_utility[1] - ip_utility
                node.regret_sum[action_str] += oop_reach * regret  # Opponent reach
        
        return (oop_utility, ip_utility)
    
    def train(self, oop_range: PokerRange, ip_range: PokerRange, 
              pot: float, stack: float, max_bets: int, iterations: int = None) -> None:
        """Train CFR solver."""
        if iterations is None:
            iterations = settings.default_iterations
            
        print(f"Training CFR solver for {iterations} iterations...")
        
        # Get hands from ranges
        oop_hands = list(oop_range.get_weighted_hands().keys())
        ip_hands = list(ip_range.get_weighted_hands().keys())
        
        if not oop_hands or not ip_hands:
            raise ValueError("Both ranges must contain at least one hand")
        
        for i in range(iterations):
            # Sample hands from ranges
            oop_hand = random.choice(oop_hands)
            ip_hand = random.choice(ip_hands)
            
            # Skip if hands conflict (same cards)
            if self._hands_conflict(oop_hand, ip_hand):
                continue
            
            # Create initial game state
            game_state = GameState(
                pot=pot,
                oop_invested=0.0,
                ip_invested=0.0,
                oop_stack=stack,
                ip_stack=stack,
                to_act=Position.OOP,  # OOP acts first
                history=[],
                street=0,
                max_bets=max_bets,
                bet_count=0
            )
            
            # Run CFR
            self.cfr(game_state, oop_hand, ip_hand, 1.0, 1.0)
            
            if (i + 1) % 100 == 0:
                print(f"Completed {i + 1} iterations")
        
        self.iterations += iterations
        print(f"Training complete! Total iterations: {self.iterations}")
    
    def _hands_conflict(self, hand1: str, hand2: str) -> bool:
        """Check if two hands share cards (simplified)."""
        # In a real implementation, you'd check actual card conflicts
        # For now, just check if hands are identical
        return hand1 == hand2
    
    def get_strategy_for_hand(self, hand: str, history: List[Action], 
                             position: Position) -> Dict[str, float]:
        """Get average strategy for specific hand and history."""
        info_set = self.get_info_set(hand, history, position)
        
        if info_set in self.nodes:
            return self.nodes[info_set].get_average_strategy()
        else:
            # Return uniform strategy if not trained
            return {"check": 0.5, "bet": 0.5} 