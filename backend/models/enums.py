"""Enums for the poker application."""
from enum import Enum


class Position(str, Enum):
    """Player positions."""
    OOP = "oop"  # Out of Position
    IP = "ip"    # In Position


class ActionType(str, Enum):
    """Types of poker actions."""
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    BET = "bet"
    RAISE = "raise"


class Street(str, Enum):
    """Poker streets."""
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class BetSize(str, Enum):
    """Standard bet sizes."""
    MIN_RAISE = "min_raise"
    POT_33 = "pot_33"
    POT_50 = "pot_50"
    POT_75 = "pot_75"
    POT_100 = "pot_100"
    POT_150 = "pot_150"
    POT_200 = "pot_200"
    ALL_IN = "all_in"


class BoardTexture(str, Enum):
    """Board texture classifications."""
    DRY = "dry"
    WET = "wet"
    PAIRED = "paired"
    CONNECTED = "connected"
    SUITED = "suited"
    HIGH_CARDS = "high_cards"
    LOW_CARDS = "low_cards" 