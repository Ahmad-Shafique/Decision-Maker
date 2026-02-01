"""Historical Analyzer - Retrospective analysis of past decisions.

This module enables analysis of historical situations to understand
what the principles framework would have recommended.

NOTE: This is a stub implementation. The full implementation will be
built in Phase 4.
"""

from typing import Optional
from pydantic import BaseModel, Field

from src.domain.situations import HistoricalSituation
from src.domain.situations import HistoricalSituation
from src.engine.models import DecisionResult
# Note: DecisionEngine is imported only for type hinting if needed, 
# but circular dependency might be an issue if we type hint the engine itself.
# We can use TYPE_CHECKING or just import the class if it doesn't import this module.
from src.engine.decision_engine import DecisionEngine


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


class HistoricalAnalyzer:
    """Analyzes past decisions against the principles framework.
    
    NOTE: This is a stub implementation. The full analysis logic
    will be built in Phase 4.
    """
    
    def __init__(self, decision_engine: DecisionEngine):
        """Initialize the analyzer.
        
        Args:
            decision_engine: The decision engine to use for recommendations.
        """
        self.engine = decision_engine
    
    def analyze(self, historical: HistoricalSituation) -> AnalysisReport:
        """Analyze a historical situation.
        
        Args:
            historical: The past situation with actual outcome.
            
        Returns:
            Complete analysis report.
        """
        # Get what principles would have recommended
        recommended = self.what_would_principles_say(historical)
        
        # Compare decisions (stub)
        gaps = self._identify_gaps(historical.actual_decision, recommended)
        lessons = self._extract_lessons(gaps)
        
        return AnalysisReport(
            situation=historical,
            actual_decision=historical.actual_decision,
            actual_outcome=historical.actual_outcome,
            recommended_decision=recommended,
            gaps=gaps,
            lessons=lessons,
            principle_adherence_score=0.5  # Stub value
        )
    
    def what_would_principles_say(
        self, situation: HistoricalSituation
    ) -> DecisionResult:
        """Get what principles would recommend for a situation.
        
        Args:
            situation: The situation to analyze.
            
        Returns:
            Decision result from the engine.
        """
        return self.engine.evaluate(situation)
    
    def _identify_gaps(
        self, actual: str, recommended: DecisionResult
    ) -> list[Gap]:
        """Identify gaps between actual and recommended decisions.
        
        Args:
            actual: The actual decision made.
            recommended: What was recommended.
            
        Returns:
            List of identified gaps.
        """
        # Stub implementation
        return [
            Gap(
                gap_type="analysis_pending",
                description="Full gap analysis to be implemented in Phase 4",
                severity=1
            )
        ]
    
    def _extract_lessons(self, gaps: list[Gap]) -> list[Lesson]:
        """Extract lessons from identified gaps.
        
        Args:
            gaps: The gaps identified.
            
        Returns:
            List of lessons learned.
        """
        # Stub implementation
        return [
            Lesson(
                insight="Full lesson extraction to be implemented in Phase 4",
                actionable="Continue building the system"
            )
        ]
