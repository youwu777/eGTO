"""Basic test to verify the modular structure works."""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported correctly."""
    try:
        # Test config
        from config.settings import settings
        print("✓ Config imported successfully")
        
        # Test models
        from models.enums import Position, ActionType
        from models.game_models import Action, GameState
        from models.api_models import SolverRequest, SolverResponse
        print("✓ Models imported successfully")
        
        # Test core
        from core.hand_evaluator import HandEvaluator
        from core.poker_range import PokerRange
        print("✓ Core modules imported successfully")
        
        # Test CFR
        from cfr.cfr_node import CFRNode
        from cfr.cfr_solver import CFRSolver
        print("✓ CFR modules imported successfully")
        
        # Test services
        from services.solver_service import SolverService
        print("✓ Services imported successfully")
        
        # Test API
        from api.routes import router
        print("✓ API modules imported successfully")
        
        # Test utils
        from utils.validators import validate_range_string, validate_game_parameters
        print("✓ Utils imported successfully")
        
        print("\n🎉 All modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality of key components."""
    try:
        # Import classes for testing
        from core.hand_evaluator import HandEvaluator
        from core.poker_range import PokerRange
        from cfr.cfr_node import CFRNode
        
        # Test hand evaluator
        evaluator = HandEvaluator()
        strength = evaluator.get_hand_strength("AA")
        assert 0.8 <= strength <= 0.9, f"Unexpected AA strength: {strength}"
        print("✓ Hand evaluator working")
        
        # Test poker range
        range_obj = PokerRange()
        range_obj.set_range_from_string("AA,KK,QQ")
        hands = range_obj.get_weighted_hands()
        assert "AA" in hands, "AA not found in range"
        print("✓ Poker range working")
        
        # Test CFR node
        node = CFRNode("test", ["check", "bet"])
        strategy = node.get_strategy(1.0)
        assert "check" in strategy, "Check action not in strategy"
        print("✓ CFR node working")
        
        print("🎉 Basic functionality tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

if __name__ == "__main__":
    print("Testing modular backend structure...\n")
    
    import_success = test_imports()
    if import_success:
        functionality_success = test_basic_functionality()
        if functionality_success:
            print("\n✅ All tests passed! The modular backend is working correctly.")
        else:
            print("\n❌ Functionality tests failed.")
    else:
        print("\n❌ Import tests failed.") 