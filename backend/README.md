# 2-Player CFR GTO Poker Solver - Backend

A modular, industrial-standard backend implementation of a 2-player Counterfactual Regret Minimization (CFR) poker solver for Game Theory Optimal (GTO) strategy calculation.

## Architecture

The backend follows a clean, modular architecture with clear separation of concerns:

```
backend/
├── config/           # Configuration management
│   ├── __init__.py
│   └── settings.py   # Application settings
├── models/           # Data models and schemas
│   ├── __init__.py
│   ├── enums.py      # Enums (Position, ActionType)
│   ├── game_models.py # Game state models
│   └── api_models.py # API request/response models
├── core/             # Core game logic
│   ├── __init__.py
│   ├── hand_evaluator.py # Hand evaluation logic
│   └── poker_range.py    # Range parsing and management
├── cfr/              # CFR implementation
│   ├── __init__.py
│   ├── cfr_node.py   # CFR node with regret matching
│   └── cfr_solver.py # Main CFR solver
├── services/         # Business logic layer
│   ├── __init__.py
│   └── solver_service.py # Solver service
├── api/              # API layer
│   ├── __init__.py
│   └── routes.py     # FastAPI routes
├── utils/            # Utilities
│   ├── __init__.py
│   └── validators.py # Validation utilities
├── main.py           # Main application entry point
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Features

- **Modular Design**: Clean separation of concerns with dedicated modules for each responsibility
- **Configuration Management**: Centralized settings with environment variable support
- **Type Safety**: Full type hints throughout the codebase
- **API Documentation**: Auto-generated OpenAPI documentation
- **Error Handling**: Comprehensive error handling and validation
- **Scalable Architecture**: Easy to extend and maintain

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python main.py
```

The server will start on `http://localhost:8000`

### API Endpoints

- `GET /api/v1/` - Root endpoint
- `POST /api/v1/solve` - Solve poker scenario
- `GET /api/v1/health` - Health check

### Example API Request

```json
{
  "oop_range": "AA-77,AKs-ATs,AKo-AJo",
  "ip_range": "AA-99,AKs-AQs,AKo-AQo",
  "starting_stack": 1000.0,
  "pot_size": 100.0,
  "bet_size": 0.75,
  "max_bets": 3
}
```

## Configuration

Configuration is managed through `config/settings.py` and supports environment variables:

- `APP_NAME` - Application name
- `APP_VERSION` - Application version
- `HOST` - Server host
- `PORT` - Server port
- `DEBUG` - Debug mode
- `DEFAULT_ITERATIONS` - Default CFR training iterations

## Development

### Adding New Features

1. **Models**: Add new data models in `models/`
2. **Core Logic**: Add game logic in `core/`
3. **Services**: Add business logic in `services/`
4. **API**: Add new endpoints in `api/routes.py`
5. **Configuration**: Add new settings in `config/settings.py`

### Testing

The modular structure makes it easy to test individual components:

```python
# Example: Testing hand evaluator
from core.hand_evaluator import HandEvaluator

evaluator = HandEvaluator()
strength = evaluator.get_hand_strength("AA")
equity = evaluator.get_equity("AA", "KK")
```

### Code Style

- Follow PEP 8 style guidelines
- Use type hints throughout
- Add docstrings for all public methods
- Keep modules focused on single responsibilities

## Dependencies

- **FastAPI**: Modern web framework for APIs
- **Pydantic**: Data validation and settings management
- **PyTorch**: Machine learning framework (for future enhancements)
- **NumPy**: Numerical computing
- **Uvicorn**: ASGI server

## Contributing

1. Follow the modular architecture
2. Add type hints to all functions
3. Include docstrings for public methods
4. Update this README for significant changes
5. Test your changes thoroughly

## License

This project is licensed under the MIT License. 