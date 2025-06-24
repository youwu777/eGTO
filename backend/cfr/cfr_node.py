"""CFR node with regret matching."""
from typing import Dict, List


class CFRNode:
    """CFR node with regret matching."""
    
    def __init__(self, info_set: str, actions: List[str]):
        self.info_set = info_set
        self.actions = actions
        self.regret_sum = {action: 0.0 for action in actions}
        self.strategy_sum = {action: 0.0 for action in actions}
        self.num_actions = len(actions)
    
    def get_strategy(self, realization_weight: float) -> Dict[str, float]:
        """Get current strategy using regret matching."""
        strategy = {}
        normalizing_sum = 0.0
        
        for action in self.actions:
            strategy[action] = max(self.regret_sum[action], 0.0)
            normalizing_sum += strategy[action]
        
        if normalizing_sum > 0:
            for action in self.actions:
                strategy[action] /= normalizing_sum
        else:
            # Uniform strategy if no positive regrets
            for action in self.actions:
                strategy[action] = 1.0 / self.num_actions
        
        # Update strategy sum
        for action in self.actions:
            self.strategy_sum[action] += realization_weight * strategy[action]
        
        return strategy
    
    def get_average_strategy(self) -> Dict[str, float]:
        """Get average strategy over all iterations."""
        avg_strategy = {}
        normalizing_sum = sum(self.strategy_sum.values())
        
        if normalizing_sum > 0:
            for action in self.actions:
                avg_strategy[action] = self.strategy_sum[action] / normalizing_sum
        else:
            for action in self.actions:
                avg_strategy[action] = 1.0 / self.num_actions
        
        return avg_strategy 