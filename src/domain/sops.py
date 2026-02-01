"""Standard Operating Procedure (SOP) domain models.

SOPs are step-by-step processes for recurring situations. They are
triggered by specific conditions and provide actionable steps.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TriggerType(str, Enum):
    """Types of conditions that can trigger an SOP."""
    
    TIME_BASED = "time_based"  # e.g., daily, weekly
    SITUATION_BASED = "situation_based"  # e.g., high-stakes decision
    EMOTIONAL = "emotional"  # e.g., feeling overwhelmed
    EXTERNAL = "external"  # e.g., receiving a suspicious request
    MANUAL = "manual"  # Explicitly invoked


class SOPStep(BaseModel):
    """A single step within an SOP.
    
    Attributes:
        number: Step number within the SOP
        instruction: What to do in this step
        is_optional: Whether this step can be skipped
        notes: Additional guidance for this step
    """
    
    number: int = Field(..., ge=1, description="Step number")
    instruction: str = Field(..., description="What to do")
    is_optional: bool = Field(default=False, description="Can this step be skipped?")
    notes: Optional[str] = Field(None, description="Additional guidance")
    
    def __str__(self) -> str:
        optional_marker = " (optional)" if self.is_optional else ""
        return f"{self.number}. {self.instruction}{optional_marker}"


class SOPTrigger(BaseModel):
    """Conditions that trigger an SOP.
    
    Attributes:
        trigger_type: The type of trigger
        condition: Description of when this trigger activates
        keywords: Keywords that indicate this trigger
    """
    
    trigger_type: TriggerType = Field(..., description="Type of trigger")
    condition: str = Field(..., description="When this trigger activates")
    keywords: list[str] = Field(default_factory=list, description="Trigger keywords")
    
    def matches_situation(self, situation_text: str) -> bool:
        """Check if situation text matches this trigger.
        
        Args:
            situation_text: Description of the situation.
            
        Returns:
            True if any keywords match.
        """
        situation_lower = situation_text.lower()
        return any(kw.lower() in situation_lower for kw in self.keywords)


class SOP(BaseModel):
    """A Standard Operating Procedure.
    
    SOPs provide step-by-step guidance for handling specific
    types of situations. They are linked to principles and
    activated by triggers.
    
    Attributes:
        id: SOP number (1-9)
        name: Descriptive name
        purpose: What principle(s) this SOP executes
        related_principle_ids: IDs of principles this SOP supports
        triggers: Conditions that activate this SOP
        steps: Ordered steps to follow
        modes: Named sub-procedures (e.g., SOP 9 has modes A, B, C)
    """
    
    id: int = Field(..., ge=1, description="SOP number")
    name: str = Field(..., min_length=1, description="SOP name")
    purpose: str = Field(..., description="What this SOP accomplishes")
    related_principle_ids: list[int] = Field(
        default_factory=list, 
        description="Principles this SOP supports"
    )
    triggers: list[SOPTrigger] = Field(
        default_factory=list, 
        description="Conditions that activate this SOP"
    )
    steps: list[SOPStep] = Field(
        default_factory=list, 
        description="Steps to follow"
    )
    modes: dict[str, list[SOPStep]] = Field(
        default_factory=dict,
        description="Named sub-procedures (for SOPs with multiple modes)"
    )
    
    def get_steps_text(self) -> str:
        """Get all steps as formatted text.
        
        Returns:
            Formatted steps as a string.
        """
        lines = []
        for step in self.steps:
            lines.append(str(step))
        return "\n".join(lines)
    
    def get_mode_steps(self, mode_name: str) -> list[SOPStep]:
        """Get steps for a specific mode.
        
        Args:
            mode_name: Name of the mode (e.g., 'A', 'B', 'C').
            
        Returns:
            List of steps for that mode, or empty list if not found.
        """
        return self.modes.get(mode_name, [])
    
    def check_triggers(self, situation_text: str) -> bool:
        """Check if this SOP should be triggered by a situation.
        
        Args:
            situation_text: Description of the situation.
            
        Returns:
            True if any trigger matches.
        """
        return any(trigger.matches_situation(situation_text) for trigger in self.triggers)
    
    def __str__(self) -> str:
        return f"SOP {self.id}: {self.name}"
    
    def __hash__(self) -> int:
        return hash(self.id)
