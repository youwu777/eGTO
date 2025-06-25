"""Comprehensive solver service for full GTO analysis."""
import time
from typing import Dict, List
from models.enums import Position, Street
from models.game_models import Action, Board, GameConfig
from models.api_models import (
    SolverRequest, SolverResponse, HandAnalysis, ConvergenceData,
    PostflopRequest, PostflopResponse, GameConfigRequest, GameConfigResponse
)
from core.poker_range import PokerRange
from cfr.comprehensive_cfr_solver import ComprehensiveCFRSolver


class ComprehensiveSolverService:
    """Service for comprehensive GTO solving with full postflop support."""
    
    def __init__(self):
        self.solver = ComprehensiveCFRSolver()
    
    def solve_comprehensive_scenario(self, request: SolverRequest) -> SolverResponse:
        """Solve comprehensive poker scenario with full game tree."""
        start_time = time.time()
        
        # Parse ranges
        oop_range = PokerRange()
        ip_range = PokerRange()
        
        oop_range.set_range_from_string(request.oop_range)
        ip_range.set_range_from_string(request.ip_range)
        
        # Create board if cards provided
        board = Board()
        if request.board_cards:
            for card in request.board_cards:
                board.add_card(card)
        
        # Create game config from user parameters
        game_config = GameConfig(
            bet_sizes=request.bet_sizes,
            max_bets_per_street=request.max_bets_per_street,
            allow_all_in=request.allow_all_in,
            min_raise_size=request.min_raise_size
        )
        
        # Train solver with convergence tracking and custom config
        training_result = self.solver.train(
            oop_range=oop_range,
            ip_range=ip_range,
            pot=request.pot_size,
            stack=request.starting_stack,
            max_bets=request.max_bets,
            iterations=request.iterations,
            game_config=game_config
        )
        
        # Get comprehensive strategies for sample hands
        oop_hands = list(oop_range.get_weighted_hands().keys())[:15]  # More hands
        ip_hands = list(ip_range.get_weighted_hands().keys())[:15]
        
        oop_strategies = {}
        ip_strategies = {}
        
        # Get opponent ranges for analysis
        oop_range_dict = oop_range.get_weighted_hands()
        ip_range_dict = ip_range.get_weighted_hands()
        
        for hand in oop_hands:
            analysis = self.solver.get_comprehensive_strategy(
                hand, [], Position.OOP, board, ip_range_dict, game_config
            )
            oop_strategies[hand] = HandAnalysis(
                strategy=analysis['strategy'],
                absolute_strength=analysis['hand_strength'].absolute_strength if analysis['hand_strength'] else None,
                relative_strength=analysis['hand_strength'].relative_strength if analysis['hand_strength'] else None,
                equity_vs_range=analysis['hand_strength'].equity_vs_range if analysis['hand_strength'] else None,
                nut_potential=analysis['hand_strength'].nut_potential if analysis['hand_strength'] else None,
                board_interaction=analysis['hand_strength'].board_interaction if analysis['hand_strength'] else None,
                blockers=analysis['hand_strength'].blockers if analysis['hand_strength'] else None,
                board_texture=analysis['board_texture'],
                pot_odds=analysis['pot_odds']
            )
        
        for hand in ip_hands:
            analysis = self.solver.get_comprehensive_strategy(
                hand, [], Position.IP, board, oop_range_dict, game_config
            )
            ip_strategies[hand] = HandAnalysis(
                strategy=analysis['strategy'],
                absolute_strength=analysis['hand_strength'].absolute_strength if analysis['hand_strength'] else None,
                relative_strength=analysis['hand_strength'].relative_strength if analysis['hand_strength'] else None,
                equity_vs_range=analysis['hand_strength'].equity_vs_range if analysis['hand_strength'] else None,
                nut_potential=analysis['hand_strength'].nut_potential if analysis['hand_strength'] else None,
                board_interaction=analysis['hand_strength'].board_interaction if analysis['hand_strength'] else None,
                blockers=analysis['hand_strength'].blockers if analysis['hand_strength'] else None,
                board_texture=analysis['board_texture'],
                pot_odds=analysis['pot_odds']
            )
        
        computation_time = time.time() - start_time
        
        # Convert convergence history
        convergence_history = [
            ConvergenceData(
                iteration=item['iteration'],
                convergence=item['convergence'],
                nodes_count=item['nodes_count']
            )
            for item in training_result['convergence_history']
        ]
        
        return SolverResponse(
            oop_strategy=oop_strategies,
            ip_strategy=ip_strategies,
            training_iterations=training_result['iterations'],
            computation_time=computation_time,
            nodes_count=training_result['nodes_count'],
            convergence_history=convergence_history,
            final_convergence=convergence_history[-1].convergence if convergence_history else 0.0,
            board_texture=board.texture.value if board.texture else None,
            bet_sizes_used=training_result['bet_sizes_used'],
            max_bets_per_street=training_result['max_bets_per_street']
        )
    
    def analyze_postflop_spot(self, request: PostflopRequest) -> PostflopResponse:
        """Analyze specific postflop spot with user-configurable parameters."""
        start_time = time.time()
        
        # Parse opponent range
        opponent_range = PokerRange()
        opponent_range.set_range_from_string(request.opponent_range)
        opponent_range_dict = opponent_range.get_weighted_hands()
        
        # Create board
        board = Board()
        for card in request.board_cards:
            board.add_card(card)
        
        # Parse action history
        history = []
        for action_str in request.action_history:
            # Simplified action parsing
            if action_str == "check":
                history.append(Action("check"))
            elif action_str == "fold":
                history.append(Action("fold"))
            elif action_str == "call":
                history.append(Action("call"))
            elif action_str.startswith("bet"):
                size = float(action_str.split("_")[1])
                history.append(Action("bet", size))
        
        # Get position
        position = Position(request.position)
        
        # Create game config for this spot
        game_config = GameConfig(
            bet_sizes=request.bet_sizes,
            max_bets_per_street={request.position: request.max_bets_remaining},
            allow_all_in=request.allow_all_in,
            min_raise_size=request.min_raise_size
        )
        
        # Get comprehensive analysis
        analysis = self.solver.get_comprehensive_strategy(
            request.hand, history, position, board, opponent_range_dict, game_config
        )
        
        # Calculate equity vs range
        equity_vs_range = self.solver.hand_evaluator.calculate_equity_vs_range(
            request.hand, opponent_range_dict, board
        )
        
        # Determine recommended action
        strategy = analysis['strategy']
        recommended_action = max(strategy.items(), key=lambda x: x[1])[0]
        confidence = strategy[recommended_action]
        
        # Calculate pot odds
        pot_odds = self._calculate_pot_odds_from_history(history, request.pot_size)
        
        # Get available actions for this spot
        available_actions = list(strategy.keys())
        bet_sizes_available = analysis['available_bet_sizes']
        
        computation_time = time.time() - start_time
        
        return PostflopResponse(
            strategy=strategy,
            hand_strength=HandAnalysis(
                strategy=strategy,
                absolute_strength=analysis['hand_strength'].absolute_strength if analysis['hand_strength'] else None,
                relative_strength=analysis['hand_strength'].relative_strength if analysis['hand_strength'] else None,
                equity_vs_range=equity_vs_range,
                nut_potential=analysis['hand_strength'].nut_potential if analysis['hand_strength'] else None,
                board_interaction=analysis['hand_strength'].board_interaction if analysis['hand_strength'] else None,
                blockers=analysis['hand_strength'].blockers if analysis['hand_strength'] else None,
                board_texture=analysis['board_texture'],
                pot_odds=pot_odds
            ),
            board_texture=board.texture.value if board.texture else "unknown",
            pot_odds=pot_odds,
            position=request.position,
            equity_vs_range=equity_vs_range,
            recommended_action=recommended_action,
            confidence=confidence,
            available_actions=available_actions,
            bet_sizes_available=bet_sizes_available
        )
    
    def validate_game_config(self, request: GameConfigRequest) -> GameConfigResponse:
        """Validate game configuration and estimate computational requirements."""
        warnings = []
        
        # Validate bet sizes
        if not request.bet_sizes:
            warnings.append("No bet sizes provided")
        elif len(request.bet_sizes) > 10:
            warnings.append("Too many bet sizes may slow down training")
        
        # Validate max bets per street
        total_max_bets = sum(request.max_bets_per_street.values())
        if total_max_bets > 10:
            warnings.append("High total max bets may create very large game trees")
        
        # Estimate computational requirements
        estimated_nodes = self._estimate_nodes(request)
        estimated_training_time = self._estimate_training_time(estimated_nodes)
        recommended_iterations = self._recommend_iterations(estimated_nodes)
        
        is_valid = len(warnings) == 0 or all("may" in warning for warning in warnings)
        
        return GameConfigResponse(
            is_valid=is_valid,
            warnings=warnings,
            estimated_nodes=estimated_nodes,
            estimated_training_time=estimated_training_time,
            recommended_iterations=recommended_iterations
        )
    
    def _estimate_nodes(self, request: GameConfigRequest) -> int:
        """Estimate number of nodes in game tree."""
        # Simplified estimation based on bet sizes and max bets
        avg_bet_sizes = len(request.bet_sizes)
        avg_max_bets = sum(request.max_bets_per_street.values()) / len(request.max_bets_per_street.values())
        
        # Rough estimation: nodes ≈ (bet_sizes * max_bets) ^ depth
        estimated_nodes = int((avg_bet_sizes * avg_max_bets) ** 3)  # 3 levels deep
        return min(estimated_nodes, 1000000)  # Cap at 1M nodes
    
    def _estimate_training_time(self, nodes: int) -> float:
        """Estimate training time in seconds."""
        # Rough estimation: 1000 nodes per second
        return nodes / 1000.0
    
    def _recommend_iterations(self, nodes: int) -> int:
        """Recommend number of training iterations."""
        # Base recommendation: 100K iterations
        base_iterations = 100000
        
        # Adjust based on game tree size
        if nodes > 100000:
            base_iterations = 200000
        elif nodes > 500000:
            base_iterations = 500000
        
        return min(base_iterations, 1000000)  # Cap at 1M iterations
    
    def _calculate_pot_odds_from_history(self, history: List[Action], pot_size: float) -> float:
        """Calculate pot odds from action history."""
        if not history:
            return float('inf')
        
        # Find the last bet
        for action in reversed(history):
            if action.type == "bet":
                return pot_size / action.size
        
        return float('inf')
    
    def get_solver_status(self) -> Dict:
        """Get comprehensive solver status."""
        return {
            "status": "healthy",
            "iterations": self.solver.iterations,
            "nodes_count": len(self.solver.nodes),
            "convergence_history_length": len(self.solver.convergence_history),
            "last_convergence": self.solver.convergence_history[-1]['convergence'] if self.solver.convergence_history else None
        } 