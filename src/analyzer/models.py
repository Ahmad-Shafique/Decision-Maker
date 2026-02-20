from typing import Optional, List
from pydantic import BaseModel, Field
from src.domain.situations import HistoricalSituation
from src.engine.models import DecisionResult

class Gap(BaseModel):
    """A gap between actual and recommended decision.
    
    Attributes:
        gap_type: Type of gap (missed_principle, wrong_priority, etc.)
        description: Details about the gap
        severity: How significant the gap is (1-10)
    """
    
    gap_type: str
    description: str
    severity: int = Field(ge=1, le=10)


class Lesson(BaseModel):
    """A lesson learned from the analysis.
    
    Attributes:
        principle_id: Related principle (if any)
        insight: The lesson learned
        actionable: Specific action to take
    """
    
    principle_id: Optional[int] = None
    insight: str
    actionable: str


class AnalysisReport(BaseModel):
    """Complete analysis of a historical situation.
    
    Attributes:
        situation: The historical situation analyzed
        actual_decision: What was actually decided
        actual_outcome: What happened as a result
        recommended_decision: What principles would have said
        gaps: Differences between actual and recommended
        lessons: Lessons learned
        principle_adherence_score: How well principles were followed (0-1)
    """
    
    situation: HistoricalSituation
    actual_decision: str
    actual_outcome: str
    recommended_decision: DecisionResult
    gaps: list[Gap] = Field(default_factory=list)
    lessons: list[Lesson] = Field(default_factory=list)
    principle_adherence_score: float = Field(ge=0, le=1)
