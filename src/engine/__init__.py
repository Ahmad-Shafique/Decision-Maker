"""Decision Engine Module.

The core logic for applying principles to situations.
"""

from src.engine.decision_engine import DecisionEngine
from src.engine.models import DecisionResult, PrincipleMatch, AlignmentScore
from src.engine.matching import MatchingStrategy, KeywordMatchingStrategy

__all__ = [
    "DecisionEngine",
    "DecisionResult",
    "PrincipleMatch",
    "AlignmentScore",
    "MatchingStrategy",
    "KeywordMatchingStrategy",
]
