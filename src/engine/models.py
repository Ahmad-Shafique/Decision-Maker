"""Decision Engine Models.

Data models used by the decision engine and matching strategies.
"""

from typing import Optional
from pydantic import BaseModel, Field

from src.domain.principles import Principle
from src.domain.situations import Situation
from src.domain.sops import SOP


class PrincipleMatch(BaseModel):
    """A matched principle with relevance score.
    
    Attributes:
        principle: The matched principle
        relevance_score: How relevant this principle is (0-1)
        match_reason: Why this principle matches
    """
    
    principle: Principle
    relevance_score: float = Field(ge=0, le=1)
    match_reason: str


class AlignmentScore(BaseModel):
    """Score indicating alignment with values.
    
    Attributes:
        overall_score: Overall alignment (0-1)
        value_scores: Per-value alignment scores
    """
    
    overall_score: float = Field(ge=0, le=1)
    value_scores: dict[str, float] = Field(default_factory=dict)


class MatchingMetadata(BaseModel):
    """Metadata about the matching process.
    
    Attributes:
        strategies_attempted: Which strategies were tried
        strategies_succeeded: Which strategies returned matches
        llm_provider_used: Which LLM provider was used for embeddings
        fallback_triggered: Whether fallback to keyword-only was needed
    """
    
    strategies_attempted: list[str] = Field(default_factory=list)
    strategies_succeeded: list[str] = Field(default_factory=list)
    llm_provider_used: Optional[str] = None
    fallback_triggered: bool = False


class DecisionResult(BaseModel):
    """Result of evaluating a situation.
    
    Attributes:
        situation: The evaluated situation
        applicable_principles: Principles that apply
        triggered_sops: SOPs that should be executed
        recommendation: Suggested action
        value_alignment: How aligned the recommendation is with values
        confidence: Confidence in the recommendation (0-1)
        reasoning: Explanation of the reasoning
        matching_metadata: Information about the matching process
    """
    
    situation: Situation
    applicable_principles: list[PrincipleMatch] = Field(default_factory=list)
    triggered_sops: list[SOP] = Field(default_factory=list)
    recommendation: str = ""
    value_alignment: Optional[AlignmentScore] = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    reasoning: str = ""
    matching_metadata: Optional[MatchingMetadata] = None
