"""Situation domain models.

Situations represent real-world scenarios that require principle
application. They can be current (needing a decision) or historical
(for analysis).
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class Stakes(str, Enum):
    """Level of stakes/importance for a situation."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Domain(str, Enum):
    """Life domain a situation belongs to."""
    
    PERSONAL = "personal"
    PROFESSIONAL = "professional"
    FAMILY = "family"
    FINANCIAL = "financial"
    HEALTH = "health"
    SOCIAL = "social"


class SituationContext(BaseModel):
    """Contextual information about a situation.
    
    Captures the facts, emotions, stakeholders, and other context
    needed to properly evaluate a situation.
    
    Attributes:
        facts: Objective facts about the situation
        emotions: Feelings associated with the situation
        stakeholders: People involved or affected
        constraints: Limitations or boundaries
        timeline: Relevant time information
        prior_actions: What has already been done
    """
    
    facts: list[str] = Field(default_factory=list, description="Objective facts")
    emotions: list[str] = Field(default_factory=list, description="Associated feelings")
    stakeholders: list[str] = Field(default_factory=list, description="People involved")
    constraints: list[str] = Field(default_factory=list, description="Limitations")
    timeline: Optional[str] = Field(None, description="Time context")
    prior_actions: list[str] = Field(default_factory=list, description="Actions already taken")
    
    def get_summary(self) -> str:
        """Get a summary of the context.
        
        Returns:
            Formatted summary string.
        """
        parts = []
        if self.facts:
            parts.append(f"Facts: {', '.join(self.facts)}")
        if self.emotions:
            parts.append(f"Emotions: {', '.join(self.emotions)}")
        if self.stakeholders:
            parts.append(f"Stakeholders: {', '.join(self.stakeholders)}")
        if self.constraints:
            parts.append(f"Constraints: {', '.join(self.constraints)}")
        return " | ".join(parts)


class Situation(BaseModel):
    """A scenario requiring principle application.
    
    Represents a current situation that needs a decision or
    analysis against the principles framework.
    
    Attributes:
        id: Unique identifier
        description: What is happening
        context: Detailed contextual information
        stakes: How high are the stakes
        domain: Which life domain this belongs to
        tags: Keywords for matching
        created_at: When this situation was recorded
    """
    
    id: str = Field(..., description="Unique identifier")
    description: str = Field(..., min_length=1, description="What is happening")
    context: SituationContext = Field(
        default_factory=SituationContext, 
        description="Contextual details"
    )
    stakes: Stakes = Field(default=Stakes.MEDIUM, description="Level of stakes")
    domain: Domain = Field(default=Domain.PERSONAL, description="Life domain")
    tags: list[str] = Field(default_factory=list, description="Keywords")
    created_at: datetime = Field(
        default_factory=datetime.now, 
        description="When recorded"
    )
    
    def get_full_description(self) -> str:
        """Get the complete situation description with context.
        
        Returns:
            Full description including context.
        """
        parts = [self.description]
        context_summary = self.context.get_summary()
        if context_summary:
            parts.append(f"Context: {context_summary}")
        return "\n".join(parts)
    
    def has_emotion(self, emotion: str) -> bool:
        """Check if situation involves a specific emotion.
        
        Args:
            emotion: The emotion to check for.
            
        Returns:
            True if this emotion is present.
        """
        return emotion.lower() in [e.lower() for e in self.context.emotions]
    
    def involves_stakeholder(self, stakeholder: str) -> bool:
        """Check if a stakeholder is involved.
        
        Args:
            stakeholder: The stakeholder to check for.
            
        Returns:
            True if this stakeholder is involved.
        """
        return stakeholder.lower() in [s.lower() for s in self.context.stakeholders]
    
    def __str__(self) -> str:
        return f"[{self.stakes.value.upper()}] {self.description[:50]}..."


class HistoricalSituation(Situation):
    """A past situation with actual decision and outcome.
    
    Extends Situation to include what actually happened,
    enabling retrospective analysis against principles.
    
    Attributes:
        actual_decision: What decision was actually made
        actual_outcome: What happened as a result
        decision_date: When the decision was made
        reflection_notes: Personal reflections on the decision
        lessons_learned: Insights gained from this experience
    """
    
    actual_decision: str = Field(..., description="What was actually decided")
    actual_outcome: str = Field(..., description="What happened as a result")
    decision_date: Optional[datetime] = Field(None, description="When decision was made")
    reflection_notes: Optional[str] = Field(None, description="Personal reflections")
    lessons_learned: list[str] = Field(default_factory=list, description="Insights gained")
    
    def get_analysis_summary(self) -> str:
        """Get a summary suitable for analysis.
        
        Returns:
            Formatted summary of the historical situation.
        """
        return (
            f"Situation: {self.description}\n"
            f"Decision: {self.actual_decision}\n"
            f"Outcome: {self.actual_outcome}"
        )
