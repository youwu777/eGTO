import sys
import os
import time
from pprint import pprint

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core import HandEvaluator, Range, GameState, GTOSolver

def test_hand_evaluation():
    """Test basic hand evaluation functionality"""
    print("Testing hand evaluation...")
    evaluator = HandEvaluator()
    
    # Test royal flush
    royal_flush = ["As", "Ks", "Qs", "Js", "Ts"]
    assert evaluator.evaluate_hand(royal_flush) > evaluator.evaluate_hand(["Kh", "Qh", "Jh", "Th", "9h"]), "Royal flush should beat straight flush"
    
    # Test four of a kind
    four_of_a_kind = ["5c", "5d", "5h", "5s", "2d"]
    full_house = ["Ac", "Ad", "Ah", "Kc", "Kd"]
    assert evaluator.evaluate_hand(four_of_a_kind) > evaluator.evaluate_hand(full_house), "Four of a kind should beat full house"
    
    print("✓ Hand evaluation tests passed!")

def test_range_parsing():
    """Test range parsing and manipulation"""
    print("\nTesting range parsing...")
    
    # Test pair range
    pair_range = Range()
    pair_range.parse_range("AA")
    assert len(pair_range.get_hands()) == 6, "AA should have 6 combinations"
    
    # Test suited range
    suited_range = Range()
    suited_range.parse_range("AKs")
    assert len(suited_range.get_hands()) == 4, "AKs should have 4 combinations"
    
    # Test offsuit range
    offsuit_range = Range()
    offsuit_range.parse_range("AKo")
    assert len(offsuit_range.get_hands()) == 12, "AKo should have 12 combinations"
    
    print("✓ Range parsing tests passed!")

def test_solver():
    """Test the GTO solver with a simple scenario"""
    print("\nTesting GTO solver...")
    
    # Set up a simple game state
    game_state = GameState(effective_stack=100.0, pot=1.0)
    
    # Define simple ranges
    ip_range = Range()
    oop_range = Range()
    
    # IP has a strong range (top 20%)
    ip_range.parse_range("AA,KK,QQ,JJ,TT,AKs,AKo")
    
    # OOP has a medium range (top 30%)
    oop_range.parse_range("AA-99,AJs+,KQs,AQo+")
    
    # Initialize solver
    solver = GTOSolver(use_gpu=False)  # Test without GPU first
    
    # Solve
    print("Solving for GTO strategies...")
    start_time = time.time()
    solution = solver.solve(
        ip_range=ip_range,
        oop_range=oop_range,
        game_state=game_state,
        max_iterations=10,  # Keep it short for testing
        accuracy=0.1
    )
    
    print(f"\nSolution found in {time.time() - start_time:.2f} seconds")
    print("\nIP Strategy:")
    pprint(solution['ip_strategy'])
    print("\nOOP Strategy:")
    pprint(solution['oop_strategy'])
    
    print("\n✓ Solver test completed!")

def main():
    """Run all tests"""
    try:
        test_hand_evaluation()
        test_range_parsing()
        test_solver()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nTest failed: {e}", file=sys.stderr)
        raise

if __name__ == "__main__":
    main()
