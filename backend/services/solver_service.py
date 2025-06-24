"""Solver service for handling poker GTO calculations."""
import time
from typing import Dict
from models.enums import Position
from models.game_models import Action
from models.api_models import SolverRequest, SolverResponse
from core.poker_range import PokerRange
from cfr.cfr_solver import CFRSolver


class SolverService:
    """Service for handling poker solver operations."""
    
    def __init__(self):
        self.solver = CFRSolver()
    
    def solve_scenario(self, request: SolverRequest) -> SolverResponse:
        """Solve a poker scenario using CFR."""
        start_time = time.time()
        
        # Parse ranges
        oop_range = PokerRange()
        ip_range = PokerRange()
        
        oop_range.set_range_from_string(request.oop_range)
        ip_range.set_range_from_string(request.ip_range)
        
        # Train solver
        self.solver.train(
            oop_range=oop_range,
            ip_range=ip_range,
            pot=request.pot_size,
            stack=request.starting_stack,
            max_bets=request.max_bets
        )
        
        # Get strategies for sample hands
        oop_hands = list(oop_range.get_weighted_hands().keys())[:10]  # Sample
        ip_hands = list(ip_range.get_weighted_hands().keys())[:10]
        
        oop_strategies = {}
        ip_strategies = {}
        
        for hand in oop_hands:
            oop_strategies[hand] = self.solver.get_strategy_for_hand(hand, [], Position.OOP)
        
        for hand in ip_hands:
            ip_strategies[hand] = self.solver.get_strategy_for_hand(hand, [], Position.IP)
        
        computation_time = time.time() - start_time
        
        return SolverResponse(
            oop_strategy=oop_strategies,
            ip_strategy=ip_strategies,
            training_iterations=self.solver.iterations,
            computation_time=computation_time
        )
    
    def get_health_status(self) -> Dict:
        """Get health status of the solver."""
        return {
            "status": "healthy",
            "iterations": self.solver.iterations,
            "nodes_count": len(self.solver.nodes)
        } 