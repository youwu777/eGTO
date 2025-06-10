# GTO Poker Solver Microservice

A high-performance Texas Hold'em GTO solver built with Python and GPU acceleration, similar to GTO+.

## Features

- Range vs Range equity calculation
- GTO solution generation for preflop, flop, turn, and river
- GPU-accelerated computations
- REST API for easy integration
- Support for multiple bet sizes and stack depths

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables in `.env`:
   ```
   PORT=8000
   DEBUG=true
   ```

3. Run the service:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

- `POST /api/solve`: Solve for GTO strategies given ranges and game parameters
- `GET /api/health`: Check service status

## Project Structure

- `main.py`: FastAPI application and endpoints
- `core/`: Core GTO solving logic
  - `solver.py`: GTO solver implementation
  - `evaluator.py`: Hand evaluation and equity calculation
  - `game_state.py`: Game state representation
  - `ranges.py`: Range manipulation and parsing
- `api/`: API endpoints and schemas
  - `schemas.py`: Pydantic models for request/response
  - `endpoints.py`: API route handlers
