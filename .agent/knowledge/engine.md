# Decision Engine Internals

## Purpose

The Decision Engine is the core component that:
1. Takes a situation as input
2. Matches it to relevant principles
3. Identifies applicable SOPs
4. Generates a recommendation with confidence scores

## Key Classes

### `DecisionEngine`
Orchestrates the decision-making process.

```python
class DecisionEngine:
    def __init__(self, knowledge_base: KnowledgeBase)
    def evaluate(self, situation: Situation) -> DecisionResult
    def get_applicable_principles(self, situation: Situation) -> List[PrincipleMatch]
    def get_applicable_sops(self, situation: Situation) -> List[SOP]
    def check_value_alignment(self, decision: str, principles: List[Principle]) -> AlignmentScore
```

### `PrincipleMatcher`
Matches situations to principles using configurable strategies.

```python
class PrincipleMatcher:
    def __init__(self, strategy: MatchingStrategy)
    def match(self, situation: Situation, principles: List[Principle]) -> List[PrincipleMatch]
```

### `SOPTriggerMatcher`
Identifies when SOPs should activate.

```python
class SOPTriggerMatcher:
    def check_triggers(self, situation: Situation, sops: List[SOP]) -> List[SOP]
```

## Decision Flow

```
Situation Input
      │
      ▼
┌─────────────────┐
│ Extract Context │  (facts, emotions, stakeholders, stakes)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Match Principles│  (keyword, tag, semantic matching)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Check SOP       │  (trigger conditions)
│ Triggers        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Evaluate Value  │  (alignment scoring)
│ Alignment       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Generate        │  (recommendation with reasoning)
│ Recommendation  │
└────────┬────────┘
         │
         ▼
   DecisionResult
```

## Matching Strategies

### KeywordMatcher
Simple keyword-based matching. Fast but less accurate.

### TagMatcher
Matches based on situation tags to principle tags.

### SemanticMatcher (Future)
Uses embeddings for meaning-based matching. Most accurate.

## Output: DecisionResult

```python
@dataclass
class DecisionResult:
    situation: Situation
    applicable_principles: List[PrincipleMatch]
    triggered_sops: List[SOP]
    recommendation: str
    value_alignment: AlignmentScore
    confidence: float
    reasoning: str
```

## Conflict Resolution

When principles conflict:
1. Check value hierarchy (Justice > Contribution > Family > Generosity)
2. Consider situation stakes
3. Apply Principle 12: "Revert to Principles When Feeling Lost"
