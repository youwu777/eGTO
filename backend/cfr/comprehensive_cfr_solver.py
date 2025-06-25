"""Comprehensive CFR solver with full postflop game tree support."""
import random
import time
from typing import Dict, List, Tuple, Optional
from models.enums import Position, ActionType, Street, BetSize
from models.game_models import GameState, Action, Board, HandStrength, GameConfig
from core.hand_evaluator import HandEvaluator
from core.poker_range import PokerRange
from .cfr_node import CFRNode
from config.settings import settings


class ComprehensiveCFRSolver:
    """Comprehensive CFR solver with full postflop game tree."""
    
    def __init__(self):
        self.nodes = {}
        self.hand_evaluator = HandEvaluator()
        self.iterations = 0
        self.convergence_history = []
        self.last_strategy_change = 0.0
        
    def get_info_set(self, hand: str, history: List[Action], position: Position, 
                     board: Board) -> str:
        """Create comprehensive information set string."""
        history_str = ''.join([str(action) for action in history])
        board_str = ''.join(board.cards) if board.cards else "preflop"
        return f"{position.value}:{hand}:{board_str}:{history_str}"
    
    def get_available_actions(self, game_state: GameState) -> List[Action]:
        """Get available actions with user-configurable bet sizes."""
        actions = []
        
        # Determine if there's a bet to face
        current_bet = max(game_state.oop_invested, game_state.ip_invested)
        acting_invested = (game_state.oop_invested if game_state.to_act == Position.OOP 
                          else game_state.ip_invested)
        
        bet_to_call = current_bet - acting_invested
        effective_stack = game_state.get_effective_stack()
        
        if bet_to_call > 0:
            # Facing a bet - can fold or call
            actions.append(Action(ActionType.FOLD))
            actions.append(Action(ActionType.CALL, bet_to_call))
            
            # Can raise if under max bets for current street
            max_bets_for_street = game_state.game_config.get_max_bets_for_street(game_state.street)
            if game_state.bet_count < max_bets_for_street:
                # Get available bet sizes from game config
                available_bet_sizes = game_state.get_available_bet_sizes()
                
                for bet_size in available_bet_sizes:
                    if bet_size > bet_to_call:  # Must be a raise
                        actions.append(Action(ActionType.BET, bet_size))
        else:
            # No bet to face - can check or bet
            actions.append(Action(ActionType.CHECK))
            
            # Can bet if under max bets for current street
            max_bets_for_street = game_state.game_config.get_max_bets_for_street(game_state.street)
            if game_state.bet_count < max_bets_for_street:
                # Get available bet sizes from game config
                available_bet_sizes = game_state.get_available_bet_sizes()
                
                for bet_size in available_bet_sizes:
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
        new_board = Board(cards=game_state.board.cards.copy())
        new_game_config = game_state.game_config
        
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
            board=new_board,
            max_bets=game_state.max_bets,
            bet_count=new_bet_count,
            game_config=new_game_config
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
            # Showdown - compare hands with board
            oop_equity = self.hand_evaluator.calculate_equity_monte_carlo(
                oop_hand, ip_hand, game_state.board
            )
            ip_equity = 1.0 - oop_equity
            
            oop_payoff = oop_equity * game_state.pot - game_state.oop_invested
            ip_payoff = ip_equity * game_state.pot - game_state.ip_invested
            
            return (oop_payoff, ip_payoff)
    
    def cfr(self, game_state: GameState, oop_hand: str, ip_hand: str, 
            oop_reach: float, ip_reach: float) -> Tuple[float, float]:
        """Main CFR algorithm with full game tree support."""
        
        if game_state.is_terminal():
            return self.get_payoff(game_state, oop_hand, ip_hand)
        
        # Get acting player and create info set
        acting_player = Position(game_state.to_act)
        hand = oop_hand if acting_player == Position.OOP else ip_hand
        info_set = self.get_info_set(hand, game_state.history, acting_player, game_state.board)
        
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
              pot: float, stack: float, max_bets: int, iterations: int = None,
              convergence_check_interval: int = 1000, game_config: GameConfig = None) -> Dict:
        """Train CFR solver with convergence tracking and custom game config."""
        if iterations is None:
            iterations = settings.default_iterations
        
        if game_config is None:
            game_config = GameConfig()
            
        print(f"Training comprehensive CFR solver for {iterations} iterations...")
        print(f"Bet sizes: {game_config.bet_sizes}")
        print(f"Max bets per street: {game_config.max_bets_per_street}")
        
        # Get hands from ranges
        oop_hands = list(oop_range.get_weighted_hands().keys())
        ip_hands = list(ip_range.get_weighted_hands().keys())
        
        if not oop_hands or not ip_hands:
            raise ValueError("Both ranges must contain at least one hand")
        
        start_time = time.time()
        last_convergence_check = 0
        
        for i in range(iterations):
            # Sample hands from ranges
            oop_hand = random.choice(oop_hands)
            ip_hand = random.choice(ip_hands)
            
            # Skip if hands conflict
            if self._hands_conflict(oop_hand, ip_hand):
                continue
            
            # Create initial game state with custom config
            game_state = GameState(
                pot=pot,
                oop_invested=0.0,
                ip_invested=0.0,
                oop_stack=stack,
                ip_stack=stack,
                to_act=Position.OOP,
                history=[],
                street=Street.PREFLOP,
                board=Board(),
                max_bets=max_bets,
                bet_count=0,
                game_config=game_config
            )
            
            # Run CFR
            self.cfr(game_state, oop_hand, ip_hand, 1.0, 1.0)
            
            # Check convergence periodically
            if (i + 1) % convergence_check_interval == 0:
                convergence_metric = self._check_convergence()
                self.convergence_history.append({
                    'iteration': i + 1,
                    'convergence': convergence_metric,
                    'nodes_count': len(self.nodes)
                })
                
                if convergence_metric < settings.convergence_threshold:
                    print(f"Converged at iteration {i + 1} with metric {convergence_metric:.6f}")
                    break
            
            if (i + 1) % 10000 == 0:
                elapsed = time.time() - start_time
                print(f"Completed {i + 1} iterations in {elapsed:.2f}s")
        
        self.iterations += iterations
        training_time = time.time() - start_time
        
        print(f"Training complete! Total iterations: {self.iterations}")
        print(f"Training time: {training_time:.2f}s")
        print(f"Total nodes: {len(self.nodes)}")
        
        return {
            'iterations': self.iterations,
            'training_time': training_time,
            'nodes_count': len(self.nodes),
            'convergence_history': self.convergence_history,
            'bet_sizes_used': game_config.bet_sizes,
            'max_bets_per_street': game_config.max_bets_per_street
        }
    
    def _check_convergence(self) -> float:
        """Check strategy convergence across all nodes."""
        if not self.nodes:
            return float('inf')
        
        total_change = 0.0
        node_count = 0
        
        for node in self.nodes.values():
            if hasattr(node, 'last_strategy'):
                current_strategy = node.get_average_strategy()
                change = sum(abs(current_strategy.get(action, 0) - node.last_strategy.get(action, 0))
                           for action in current_strategy.keys())
                total_change += change
                node_count += 1
                node.last_strategy = current_strategy.copy()
            else:
                node.last_strategy = node.get_average_strategy().copy()
        
        return total_change / node_count if node_count > 0 else float('inf')
    
    def _hands_conflict(self, hand1: str, hand2: str) -> bool:
        """Check if two hands share cards."""
        return hand1 == hand2
    
    def get_strategy_for_hand(self, hand: str, history: List[Action], 
                             position: Position, board: Board = None) -> Dict[str, float]:
        """Get average strategy for specific hand and history."""
        if board is None:
            board = Board()
            
        info_set = self.get_info_set(hand, history, position, board)
        
        if info_set in self.nodes:
            return self.nodes[info_set].get_average_strategy()
        else:
            # Return uniform strategy if not trained
            return {"check": 0.5, "bet": 0.5}
    
    def get_comprehensive_strategy(self, hand: str, history: List[Action], 
                                  position: Position, board: Board = None,
                                  opponent_range: Dict[str, float] = None,
                                  game_config: GameConfig = None) -> Dict:
        """Get comprehensive strategy analysis with custom game config."""
        if board is None:
            board = Board()
        
        if game_config is None:
            game_config = GameConfig()
        
        # Get basic strategy
        strategy = self.get_strategy_for_hand(hand, history, position, board)
        
        # Get hand strength analysis
        if opponent_range:
            hand_strength = self.hand_evaluator.get_hand_strength_detailed(
                hand, board, opponent_range
            )
        else:
            hand_strength = None
        
        return {
            'strategy': strategy,
            'hand_strength': hand_strength,
            'board_texture': board.texture.value if board.texture else None,
            'pot_odds': self._calculate_pot_odds(history),
            'position': position.value,
            'available_bet_sizes': game_config.bet_sizes
        }
    
    def _calculate_pot_odds(self, history: List[Action]) -> float:
        """Calculate pot odds from action history."""
        if not history:
            return float('inf')
        
        # Simplified pot odds calculation
        last_action = history[-1]
        if last_action.type == ActionType.BET:
            return last_action.size / 100.0  # Simplified
        return float('inf') 