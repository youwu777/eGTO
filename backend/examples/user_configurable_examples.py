"""Examples of using user-configurable bet sizes and max bets per street."""
import requests
import json
from typing import Dict, List


def example_1_basic_custom_bet_sizes():
    """Example 1: Basic custom bet sizes."""
    print("=== Example 1: Basic Custom Bet Sizes ===")
    
    request = {
        "oop_range": "AA-77,AKs-ATs,AKo-AJo",
        "ip_range": "AA-99,AKs-AQs,AKo-AQo",
        "starting_stack": 1000.0,
        "pot_size": 100.0,
        "max_bets": 3,
        "iterations": 50000,
        # Custom bet sizes: only 50% and 100% pot
        "bet_sizes": [0.5, 1.0],
        "max_bets_per_street": {
            "preflop": 3,
            "flop": 2,
            "turn": 1,
            "river": 1
        },
        "allow_all_in": True,
        "min_raise_size": 0.5
    }
    
    print("Request:")
    print(json.dumps(request, indent=2))
    
    # In real usage, you would make the API call:
    # response = requests.post("http://localhost:8000/api/v1/solve/comprehensive", json=request)
    # print("Response:", response.json())


def example_2_aggressive_betting():
    """Example 2: Aggressive betting with many bet sizes."""
    print("\n=== Example 2: Aggressive Betting ===")
    
    request = {
        "oop_range": "AA-55,AKs-A8s,AKo-A9o",
        "ip_range": "AA-88,AKs-A9s,AKo-ATo",
        "starting_stack": 1000.0,
        "pot_size": 100.0,
        "max_bets": 4,
        "iterations": 100000,
        # Many bet sizes for aggressive play
        "bet_sizes": [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0],
        "max_bets_per_street": {
            "preflop": 4,
            "flop": 3,
            "turn": 2,
            "river": 1
        },
        "allow_all_in": True,
        "min_raise_size": 0.25
    }
    
    print("Request:")
    print(json.dumps(request, indent=2))


def example_3_conservative_play():
    """Example 3: Conservative play with limited betting."""
    print("\n=== Example 3: Conservative Play ===")
    
    request = {
        "oop_range": "AA-99,AKs-AJs,AKo-AQo",
        "ip_range": "AA-TT,AKs-AQs,AKo-AQo",
        "starting_stack": 1000.0,
        "pot_size": 100.0,
        "max_bets": 2,
        "iterations": 50000,
        # Conservative bet sizes
        "bet_sizes": [0.5, 0.75],
        "max_bets_per_street": {
            "preflop": 2,
            "flop": 1,
            "turn": 1,
            "river": 1
        },
        "allow_all_in": False,  # No all-in allowed
        "min_raise_size": 0.5
    }
    
    print("Request:")
    print(json.dumps(request, indent=2))


def example_4_postflop_analysis():
    """Example 4: Postflop analysis with custom parameters."""
    print("\n=== Example 4: Postflop Analysis ===")
    
    request = {
        "hand": "AA",
        "position": "oop",
        "board_cards": ["Ah", "Ks", "Qd"],
        "opponent_range": "AA-99,AKs-AQs,AKo-AQo",
        "pot_size": 150.0,
        "stack_size": 1000.0,
        "action_history": ["bet_75.0", "call"],
        # Custom bet sizes for this spot
        "bet_sizes": [0.5, 1.0, 1.5],
        "max_bets_remaining": 2,
        "allow_all_in": True,
        "min_raise_size": 0.5
    }
    
    print("Request:")
    print(json.dumps(request, indent=2))


def example_5_validate_config():
    """Example 5: Validate game configuration."""
    print("\n=== Example 5: Validate Game Configuration ===")
    
    request = {
        "bet_sizes": [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0],
        "max_bets_per_street": {
            "preflop": 4,
            "flop": 3,
            "turn": 2,
            "river": 1
        },
        "starting_stack": 1000.0,
        "pot_size": 100.0
    }
    
    print("Request:")
    print(json.dumps(request, indent=2))
    
    # In real usage:
    # response = requests.post("http://localhost:8000/api/v1/validate/config", json=request)
    # print("Validation Response:", response.json())


def example_6_tournament_style():
    """Example 6: Tournament-style play with ICM considerations."""
    print("\n=== Example 6: Tournament Style ===")
    
    request = {
        "oop_range": "AA-22,AKs-A2s,AKo-A2o,KQs-K2s,KQo-K2o",
        "ip_range": "AA-33,AKs-A3s,AKo-A3o,KQs-K3s,KQo-K3o",
        "starting_stack": 500.0,  # Shorter stacks
        "pot_size": 50.0,
        "max_bets": 3,
        "iterations": 75000,
        # Tournament-style bet sizes
        "bet_sizes": [0.33, 0.5, 0.75, 1.0, 1.5],
        "max_bets_per_street": {
            "preflop": 3,
            "flop": 2,
            "turn": 1,
            "river": 1
        },
        "allow_all_in": True,
        "min_raise_size": 0.33
    }
    
    print("Request:")
    print(json.dumps(request, indent=2))


def example_7_cash_game_deep_stacks():
    """Example 7: Cash game with deep stacks."""
    print("\n=== Example 7: Cash Game Deep Stacks ===")
    
    request = {
        "oop_range": "AA-55,AKs-A8s,AKo-A9o,KQs-K9s,KQo-KTo",
        "ip_range": "AA-77,AKs-A9s,AKo-ATo,KQs-KTs,KQo-KJo",
        "starting_stack": 2000.0,  # Deep stacks
        "pot_size": 100.0,
        "max_bets": 4,
        "iterations": 100000,
        # Deep stack bet sizes
        "bet_sizes": [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0],
        "max_bets_per_street": {
            "preflop": 4,
            "flop": 3,
            "turn": 2,
            "river": 2
        },
        "allow_all_in": True,
        "min_raise_size": 0.25
    }
    
    print("Request:")
    print(json.dumps(request, indent=2))


def example_8_heads_up_specific():
    """Example 8: Heads-up specific configuration."""
    print("\n=== Example 8: Heads-Up Specific ===")
    
    request = {
        "oop_range": "AA-22,AKs-A2s,AKo-A2o,KQs-K2s,KQo-K2o,QJs-Q2s,QJo-Q2o",
        "ip_range": "AA-22,AKs-A2s,AKo-A2o,KQs-K2s,KQo-K2o,QJs-Q2s,QJo-Q2o",
        "starting_stack": 1000.0,
        "pot_size": 100.0,
        "max_bets": 4,
        "iterations": 100000,
        # Heads-up specific bet sizes
        "bet_sizes": [0.33, 0.5, 0.75, 1.0, 1.5, 2.0],
        "max_bets_per_street": {
            "preflop": 4,
            "flop": 3,
            "turn": 2,
            "river": 1
        },
        "allow_all_in": True,
        "min_raise_size": 0.33
    }
    
    print("Request:")
    print(json.dumps(request, indent=2))


def compare_configurations():
    """Compare different configurations and their impact."""
    print("\n=== Configuration Comparison ===")
    
    configs = {
        "Conservative": {
            "bet_sizes": [0.5, 0.75],
            "max_bets_per_street": {"preflop": 2, "flop": 1, "turn": 1, "river": 1},
            "estimated_nodes": 1000,
            "training_time": 30
        },
        "Standard": {
            "bet_sizes": [0.33, 0.5, 0.75, 1.0, 1.5, 2.0],
            "max_bets_per_street": {"preflop": 4, "flop": 3, "turn": 2, "river": 1},
            "estimated_nodes": 50000,
            "training_time": 120
        },
        "Aggressive": {
            "bet_sizes": [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0],
            "max_bets_per_street": {"preflop": 4, "flop": 3, "turn": 2, "river": 2},
            "estimated_nodes": 200000,
            "training_time": 300
        }
    }
    
    print("Configuration Impact Comparison:")
    for name, config in configs.items():
        print(f"\n{name}:")
        print(f"  Bet sizes: {config['bet_sizes']}")
        print(f"  Max bets: {config['max_bets_per_street']}")
        print(f"  Estimated nodes: {config['estimated_nodes']:,}")
        print(f"  Training time: ~{config['training_time']} seconds")


def main():
    """Run all examples."""
    print("User-Configurable GTO Solver Examples")
    print("=" * 50)
    
    example_1_basic_custom_bet_sizes()
    example_2_aggressive_betting()
    example_3_conservative_play()
    example_4_postflop_analysis()
    example_5_validate_config()
    example_6_tournament_style()
    example_7_cash_game_deep_stacks()
    example_8_heads_up_specific()
    compare_configurations()
    
    print("\n" + "=" * 50)
    print("Key Benefits of User-Configurable Parameters:")
    print("1. Customize bet sizes for your playing style")
    print("2. Control game tree size and training time")
    print("3. Adapt to different game formats (cash vs tournament)")
    print("4. Optimize for specific stack depths")
    print("5. Validate configurations before training")
    print("6. Get realistic GTO strategies for your specific game")


if __name__ == "__main__":
    main() 