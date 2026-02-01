# Historical Analyzer Internals

## Purpose

The Historical Analyzer enables retrospective analysis:
1. Take a past situation with actual outcome
2. Determine what principles would have recommended
3. Compare actual vs recommended decision
4. Identify gaps and learning opportunities

## Key Classes

### `HistoricalAnalyzer`
Main class for historical analysis.

```python
class HistoricalAnalyzer:
    def __init__(self, decision_engine: DecisionEngine)
    def analyze(self, historical_situation: HistoricalSituation) -> AnalysisReport
    def what_would_principles_say(self, situation: Situation) -> DecisionResult
    def compare_decisions(self, actual: str, recommended: DecisionResult) -> GapAnalysis
```

### `PatternDetector`
Identifies recurring patterns across situations.

```python
class PatternDetector:
    def detect_patterns(self, situations: List[HistoricalSituation]) -> List[Pattern]
    def find_principle_adherence_trends(self) -> AdherenceTrend
    def suggest_principle_refinements(self) -> List[Refinement]
```

## Analysis Flow

```
Historical Situation
(with actual decision & outcome)
         │
         ▼
┌─────────────────────┐
│ Run Decision Engine │  (get what principles would say)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Compare Decisions   │  (actual vs recommended)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Identify Gaps       │  (missed principles, wrong priorities)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Generate Insights   │  (lessons learned)
└──────────┬──────────┘
           │
           ▼
     AnalysisReport
```

## Output: AnalysisReport

```python
@dataclass
class AnalysisReport:
    situation: HistoricalSituation
    actual_decision: str
    actual_outcome: str
    recommended_decision: DecisionResult
    gaps: List[Gap]
    lessons: List[Lesson]
    principle_adherence_score: float
```

## Gap Types

- **MissedPrinciple**: A principle applied but was ignored
- **WrongPriority**: Principles were applied in wrong order
- **SkippedSOP**: An SOP should have been triggered
- **EmotionalOverride**: Emotion overrode principle-based logic
- **InformationGap**: Decision made without full information

## Pattern Detection

The system can analyze multiple historical situations to find:
- Recurring principle violations
- Common emotional triggers
- Areas needing principle refinement
- Strengths (consistently followed principles)

## Historical Data Format

```yaml
# data/historical_situations/2024-01-meeting.yaml
id: "2024-01-meeting"
date: "2024-01-15"
description: "Difficult negotiation with vendor"
context:
  facts:
    - "Vendor demanding 40% price increase"
    - "No alternative vendors available short-term"
  emotions:
    - "Frustrated"
    - "Pressured"
  stakeholders:
    - "Vendor rep"
    - "My team"
  stakes: "high"
  domain: "professional"
actual_decision: "Agreed to increase without negotiation"
actual_outcome: "Budget overrun, regret"
```
