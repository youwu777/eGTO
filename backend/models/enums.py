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