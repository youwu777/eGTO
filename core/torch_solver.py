import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional
import time

from .evaluator import HandEvaluator, Range, GameState

class GTONetwork(nn.Module):
    """Neural network for estimating counterfactual values"""
    def __init__(self, input_dim: int, hidden_dims: List[int] = [256, 128, 64]):
        super(GTONetwork, self).__init__()
        layers = []
        prev_dim = input_dim
        
        # Create hidden layers
        for dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            prev_dim = dim
        
        # Output layer: 3 actions (fold, call, raise)
        layers.append(nn.Linear(prev_dim, 3))
        self.network = nn.Sequential(*layers)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)

class TorchGTOSolver:
    def __init__(self, evaluator: Optional[HandEvaluator] = None, 
                 use_gpu: bool = True):
        self.evaluator = evaluator or HandEvaluator()
        
        # Determine the best available device
        if use_gpu and torch.backends.mps.is_available():
            self.device = torch.device("mps")
            print("Using MPS (Metal) for GPU acceleration")
        elif use_gpu and torch.cuda.is_available():
            self.device = torch.device("cuda")
            print("Using CUDA for GPU acceleration")
        else:
            self.device = torch.device("cpu")
            print("Using CPU (no GPU acceleration available)")
        
        # Initialize networks for each player
        input_dim = 100  # Dimension of the game state representation
        self.ip_network = GTONetwork(input_dim).to(self.device)
        self.oop_network = GTONetwork(input_dim).to(self.device)
        print(f"Models initialized on device: {self.device}")
        
        self.optimizer_ip = torch.optim.Adam(self.ip_network.parameters(), lr=0.001)
        self.optimizer_oop = torch.optim.Adam(self.oop_network.parameters(), lr=0.001)
        
        # Store strategies and regrets
        self.regret_matching_plus = True
        self.average_strategies = {}
    
    def solve(self, ip_range: Range, oop_range: Range, 
              game_state: GameState, max_iterations: int = 100,
              accuracy: float = 1e-4) -> Dict:
        """
        Solve for GTO strategies using PyTorch-accelerated CFR
        """
        start_time = time.time()
        
        # Convert ranges to tensor format
        ip_hands = list(ip_range.get_hands().keys())
        oop_hands = list(oop_range.get_hands().keys())
        
        # Initialize strategy profiles
        ip_strategy = self._initialize_strategy(ip_hands)
        oop_strategy = self._initialize_strategy(oop_hands)
        
        # Main training loop
        for iteration in range(max_iterations):
            # Update strategies using neural network
            self._update_strategies(ip_strategy, oop_strategy, game_state)
            
            # Calculate exploitability
            if iteration % 10 == 0:
                exploitability = self._calculate_exploitability(ip_strategy, oop_strategy, game_state)
                if exploitability < accuracy:
                    break
        
        # Convert strategies to a more readable format
        solution = self._format_solution(ip_strategy, oop_strategy, game_state)
        solution['solving_time'] = time.time() - start_time
        solution['iterations'] = iteration + 1
        solution['converged'] = (exploitability < accuracy)
        
        return solution
    
    def _initialize_strategy(self, hands: List[str]) -> Dict:
        """Initialize strategy with uniform distribution"""
        return {hand: torch.ones(3, device=self.device) / 3 for hand in hands}
    
    def _update_strategies(self, ip_strategy: Dict, oop_strategy: Dict, 
                         game_state: GameState) -> None:
        """Update strategies using neural network"""
        # Get game state representation
        state_rep = self._get_state_representation(game_state)
        state_tensor = torch.FloatTensor(state_rep).to(self.device).unsqueeze(0)
        
        # Forward pass through networks
        with torch.no_grad():
            ip_logits = self.ip_network(state_tensor).squeeze(0)
            oop_logits = self.oop_network(state_tensor).squeeze(0)
        
        # Update IP strategy
        for hand in ip_strategy.keys():
            ip_strategy[hand] = F.softmax(ip_logits, dim=0)
        
        # Update OOP strategy
        for hand in oop_strategy.keys():
            oop_strategy[hand] = F.softmax(oop_logits, dim=0)
    
    def _get_state_representation(self, game_state: GameState) -> np.ndarray:
        """Convert game state to a fixed-size vector representation"""
        # This is a simplified version - in practice, you'd want to include:
        # - Pot odds
        # - Effective stack to pot ratio
        # - Current street
        # - Board texture
        # - Position
        rep = np.zeros(100)  # Fixed-size representation
        
        # Encode board cards
        for i, card in enumerate(game_state.board):
            rep[i * 2] = self._card_to_value(card[0]) / 14.0  # Rank
            rep[i * 2 + 1] = self._suit_to_value(card[1]) / 4.0  # Suit
        
        # Encode pot and stack information
        rep[10] = game_state.pot / 1000.0
        rep[11] = game_state.effective_stack / 1000.0
        
        # Encode street
        street_map = {"preflop": 0, "flop": 0.25, "turn": 0.5, "river": 0.75, "showdown": 1.0}
        rep[12] = street_map.get(game_state.current_street, 0)
        
        return rep
    
    def _card_to_value(self, rank: str) -> float:
        """Convert card rank to numerical value"""
        rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
                   '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        return rank_map.get(rank.upper(), 0)
    
    def _suit_to_value(self, suit: str) -> float:
        """Convert suit to numerical value"""
        suit_map = {'c': 0, 'd': 1, 'h': 2, 's': 3}
        return suit_map.get(suit.lower(), 0)
    
    def _calculate_exploitability(self, ip_strategy: Dict, oop_strategy: Dict,
                                game_state: GameState) -> float:
        """Calculate exploitability of the current strategy profile"""
        # In a full implementation, this would calculate how much a perfectly
        # exploitative opponent could gain by deviating from the strategy
        return 0.0  # Placeholder
    
    def _format_solution(self, ip_strategy: Dict, oop_strategy: Dict,
                        game_state: GameState) -> Dict:
        """Format the solution for API response"""
        def process_strategy(strat):
            return {hand: {
                'fold': float(probs[0]),
                'call': float(probs[1]),
                'raise': float(probs[2])
            } for hand, probs in strat.items()}
        
        return {
            'ip_strategy': process_strategy(ip_strategy),
            'oop_strategy': process_strategy(oop_strategy),
            'equity_ip': 0.5,  # Placeholder
            'equity_oop': 0.5,  # Placeholder
            'exploitability': 0.0  # Placeholder
        }
