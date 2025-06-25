# Comprehensive 2-Player CFR GTO Poker Solver

A production-ready Game Theory Optimal (GTO) poker solver using Counterfactual Regret Minimization (CFR) with full postflop game tree support and **user-configurable bet sizes and max bets per street**.

## 🚀 Key Features

### Core Capabilities
- **Full Postflop Game Tree**: Complete support for preflop, flop, turn, and river
- **Monte Carlo Equity Calculations**: Accurate hand strength evaluation
- **Convergence Tracking**: Real-time monitoring of solver convergence
- **Board Texture Analysis**: Automatic classification of board textures
- **Hand Strength Analysis**: Detailed equity and nut potential calculations

### User-Configurable Parameters ⭐ NEW
- **Custom Bet Sizes**: Define your own bet sizes as fractions of pot
- **Max Bets Per Street**: Control how many bets/raises are allowed per street
- **All-in Options**: Enable/disable all-in as a betting option
- **Minimum Raise Sizes**: Set minimum raise requirements
- **Game Configuration Validation**: Validate your settings before training

### Advanced Features
- **Range vs Range Analysis**: Compare hand ranges against each other
- **Position-Based Strategies**: Different strategies for OOP vs IP
- **Comprehensive Hand Analysis**: Blockers, board interaction, nut potential
- **Real-time API**: Fast REST API for integration

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd backend

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

## 🎯 Quick Start

### Basic Usage with Default Settings

```python
import requests

# Basic solve with default bet sizes
request = {
    "oop_range": "AA-77,AKs-ATs,AKo-AJo",
    "ip_range": "AA-99,AKs-AQs,AKo-AQo",
    "starting_stack": 1000.0,
    "pot_size": 100.0,
    "max_bets": 3,
    "iterations": 50000
}

response = requests.post("http://localhost:8000/api/v1/solve/comprehensive", json=request)
print(response.json())
```

### Custom Bet Sizes and Max Bets

```python
# Custom configuration for aggressive play
request = {
    "oop_range": "AA-55,AKs-A8s,AKo-A9o",
    "ip_range": "AA-88,AKs-A9s,AKo-ATo",
    "starting_stack": 1000.0,
    "pot_size": 100.0,
    "max_bets": 4,
    "iterations": 100000,
    # Custom bet sizes: 25%, 50%, 75%, 100%, 150%, 200%, 300% of pot
    "bet_sizes": [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0],
    # Custom max bets per street
    "max_bets_per_street": {
        "preflop": 4,
        "flop": 3,
        "turn": 2,
        "river": 1
    },
    "allow_all_in": True,
    "min_raise_size": 0.25
}

response = requests.post("http://localhost:8000/api/v1/solve/comprehensive", json=request)
```

### Conservative Play Configuration

```python
# Conservative configuration with limited betting
request = {
    "oop_range": "AA-99,AKs-AJs,AKo-AQo",
    "ip_range": "AA-TT,AKs-AQs,AKo-AQo",
    "starting_stack": 1000.0,
    "pot_size": 100.0,
    "max_bets": 2,
    "iterations": 50000,
    # Only 50% and 75% pot bets
    "bet_sizes": [0.5, 0.75],
    # Limited betting per street
    "max_bets_per_street": {
        "preflop": 2,
        "flop": 1,
        "turn": 1,
        "river": 1
    },
    "allow_all_in": False,  # No all-in allowed
    "min_raise_size": 0.5
}
```

## 🔧 API Endpoints

### 1. Comprehensive Solver
```http
POST /api/v1/solve/comprehensive
```

**Request Parameters:**
- `oop_range` (string): OOP player's range
- `ip_range` (string): IP player's range
- `starting_stack` (float): Starting stack size
- `pot_size` (float): Initial pot size
- `max_bets` (int): Maximum number of bets/raises
- `iterations` (int, optional): Training iterations (default: 100,000)
- `board_cards` (list, optional): Board cards for postflop analysis
- `street` (string, optional): Current street (preflop/flop/turn/river)

**User-Configurable Parameters:**
- `bet_sizes` (list, optional): Custom bet sizes as fractions of pot (default: [0.33, 0.5, 0.75, 1.0, 1.5, 2.0])
- `max_bets_per_street` (dict, optional): Max bets per street (default: {"preflop": 4, "flop": 3, "turn": 2, "river": 1})
- `allow_all_in` (bool, optional): Allow all-in as betting option (default: True)
- `min_raise_size` (float, optional): Minimum raise size as fraction of pot (default: 0.5)

### 2. Postflop Analysis
```http
POST /api/v1/analyze/postflop
```

**Request Parameters:**
- `hand` (string): Player's hand
- `position` (string): Player position ("oop" or "ip")
- `board_cards` (list): Board cards
- `opponent_range` (string): Opponent's range
- `pot_size` (float): Current pot size
- `stack_size` (float): Stack size
- `action_history` (list, optional): Action history
- `bet_sizes` (list, optional): Available bet sizes for this spot
- `max_bets_remaining` (int, optional): Max bets remaining in this street
- `allow_all_in` (bool, optional): Allow all-in as option
- `min_raise_size` (float, optional): Minimum raise size

### 3. Game Configuration Validation ⭐ NEW
```http
POST /api/v1/validate/config
```

**Request Parameters:**
- `bet_sizes` (list): Bet sizes to validate
- `max_bets_per_street` (dict): Max bets per street
- `starting_stack` (float): Starting stack
- `pot_size` (float): Pot size

**Response:**
- `is_valid` (bool): Whether configuration is valid
- `warnings` (list): Any warnings about the configuration
- `estimated_nodes` (int): Estimated number of nodes in game tree
- `estimated_training_time` (float): Estimated training time in seconds
- `recommended_iterations` (int): Recommended number of training iterations

### 4. Health Check
```http
GET /api/v1/health/comprehensive
```

### 5. Solver Information
```http
GET /api/v1/info
```

## 🎮 Configuration Examples

### Tournament Style
```python
# Tournament with shorter stacks and ICM considerations
config = {
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
```

### Cash Game Deep Stacks
```python
# Deep stack cash game with many bet sizes
config = {
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
```

### Heads-Up Specific
```python
# Heads-up with wider ranges and more action
config = {
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
```

## 📊 Performance Impact

| Configuration | Bet Sizes | Max Bets | Estimated Nodes | Training Time |
|---------------|-----------|----------|-----------------|---------------|
| Conservative  | 2         | 5 total  | ~1,000          | ~30 seconds   |
| Standard      | 6         | 10 total | ~50,000         | ~2 minutes    |
| Aggressive    | 8         | 11 total | ~200,000        | ~5 minutes    |

## 🔍 Example Responses

### Comprehensive Solver Response
```json
{
  "oop_strategy": {
    "AA": {
      "strategy": {"check": 0.1, "bet_50.0": 0.6, "bet_100.0": 0.3},
      "absolute_strength": 0.95,
      "equity_vs_range": 0.78,
      "nut_potential": 0.85,
      "board_interaction": 0.92,
      "blockers": ["Ah", "Ad"],
      "board_texture": "high_cards",
      "pot_odds": 2.0
    }
  },
  "ip_strategy": {...},
  "training_iterations": 100000,
  "computation_time": 120.5,
  "nodes_count": 45678,
  "convergence_history": [...],
  "final_convergence": 0.0008,
  "board_texture": "high_cards",
  "bet_sizes_used": [0.33, 0.5, 0.75, 1.0, 1.5, 2.0],
  "max_bets_per_street": {"preflop": 4, "flop": 3, "turn": 2, "river": 1}
}
```

### Configuration Validation Response
```json
{
  "is_valid": true,
  "warnings": ["High total max bets may create very large game trees"],
  "estimated_nodes": 150000,
  "estimated_training_time": 180.5,
  "recommended_iterations": 200000
}
```

## 🛠️ Development

### Project Structure
```
backend/
├── config/                 # Configuration settings
├── models/                 # Data models and enums
├── core/                   # Core poker logic
├── cfr/                    # CFR implementation
├── services/               # Business logic services
├── api/                    # FastAPI routes
├── utils/                  # Utility functions
├── examples/               # Usage examples
├── main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_cfr_solver.py
```

### Adding New Bet Sizes
The solver supports any bet sizes you specify. Common patterns:

```python
# Small ball (25%, 50%, 75%)
bet_sizes = [0.25, 0.5, 0.75]

# Standard (33%, 50%, 75%, 100%, 150%, 200%)
bet_sizes = [0.33, 0.5, 0.75, 1.0, 1.5, 2.0]

# Aggressive (25%, 50%, 75%, 100%, 150%, 200%, 300%, 400%)
bet_sizes = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0]

# Custom sizes for specific spots
bet_sizes = [0.4, 0.8, 1.2, 2.5]
```

## 🎯 Best Practices

1. **Start Conservative**: Begin with fewer bet sizes and max bets
2. **Validate Configurations**: Use the validation endpoint before training
3. **Monitor Convergence**: Check convergence history for optimal training
4. **Adapt to Game Type**: Use different configurations for cash vs tournament
5. **Consider Stack Depth**: Adjust bet sizes based on effective stack size

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the examples in `examples/`
2. Review the API documentation
3. Open an issue on GitHub

---

**Note**: This solver provides educational GTO strategies. For real money play, always consider additional factors like player tendencies, game dynamics, and bankroll management. 