# Phase 4: SOP Display Fix + Historic Analyzer

**Status:** Ready for Implementation  
**Prerequisites:** Phase 2 Complete (Engine, matching, API, dashboard working)

---

## Architecture Principles Applied

| Pattern | Application |
|---------|-------------|
| **Module structure** (`models.py`, `service.py`, `__init__.py`) | Extract analyzer models; new `WhatIfAnalyzer` in own file |
| **Strategy pattern** | `WhatIfAnalyzer` accepts `DecisionEngine` via constructor injection |
| **Factory pattern** | `KnowledgeBaseFactory` for building KBs from different sources |
| **Single Responsibility** | `WhatIfAnalyzer` ≠ `HistoricalAnalyzer` — different concerns |
| **Thin Interface Layer** | API delegates to services — no business logic in endpoints |
| **Pydantic BaseModel** | All models extend BaseModel |

---

## Part 1: Bug Fix — SOP Display Incomplete

### Problem
SOPs are fully loaded (steps, modes) and returned in `DecisionResult.triggered_sops`, but:
- `decision_engine.py` `_generate_reasoning()` only mentions SOP names
- `app.js` `renderResults()` only shows `name` and `purpose`

### Fix

#### [MODIFY] `src/engine/decision_engine.py`
Expand `_generate_reasoning()` to include SOP steps and modes in recommendation.

#### [MODIFY] `src/interfaces/static/app.js`
Render SOP steps as ordered list, modes as collapsible `<details>`.

#### [MODIFY] `src/interfaces/static/style.css`
Add `.sop-steps`, `.sop-modes`, `details/summary` styles.

---

## Part 2: Historic Analyzer API & UI

### New Classes

```
WhatIfAnalyzer (new service)           KnowledgeBaseFactory (new utility)
├── analyze(situation, custom_principles?)  ├── from_yaml(data_path) → KB
│   → DecisionResult                        └── from_principles(principles, sops?, values?) → KB
└── Uses: DecisionEngine, KnowledgeBaseFactory
```

### Files to Create

#### [NEW] `src/analyzer/models.py`
Extract `Gap`, `Lesson`, `AnalysisReport` from `historical_analyzer.py`.

#### [NEW] `src/analyzer/whatif_analyzer.py`
```python
class WhatIfAnalyzer:
    def __init__(self, decision_engine: DecisionEngine): ...
    def analyze(self, situation: Situation, custom_principles: list[Principle] = None) -> DecisionResult: ...
```

### Files to Modify

#### [MODIFY] `src/analyzer/historical_analyzer.py`
Import models from `models.py`. No new methods.

#### [MODIFY] `src/analyzer/__init__.py`
Export: `HistoricalAnalyzer`, `WhatIfAnalyzer`, `Gap`, `Lesson`, `AnalysisReport`

#### [MODIFY] `src/knowledge/knowledge_base.py`
Add `KnowledgeBaseFactory` class with `from_yaml()` and `from_principles()` static methods.

#### [MODIFY] `src/interfaces/api.py`
Add endpoints:
- `POST /analyze/whatif` — delegates to `WhatIfAnalyzer`
- `POST /analyze/historical` — delegates to `HistoricalAnalyzer`
- `GET /sops` — returns all SOPs
- `GET /sops/{id}` — returns specific SOP

Initialize services in `lifespan()`:
```python
analyzer = HistoricalAnalyzer(decision_engine=engine)
whatif = WhatIfAnalyzer(decision_engine=engine)
```

#### [MODIFY] `src/interfaces/static/index.html`
Add tabbed navigation: Analyze | Historic Analyzer

#### [MODIFY] `src/interfaces/static/app.js`
Tab switching + `/analyze/whatif` and `/analyze/historical` handlers + result rendering

#### [MODIFY] `src/interfaces/static/style.css`
Tab styles + analyzer result styles

#### [MODIFY] `.agent/knowledge/interfaces.md`
Document new endpoints

### Custom Principles Format (JSON)
```json
[{"id": 1, "title": "...", "tags": [...], "sub_principles": [], "related_value_ids": [], "related_sop_ids": [], "categories": []}]
```

---

## Testing

### New Tests
| File | Test | Purpose |
|------|------|---------|
| `test_analyzer.py` | `test_whatif_default_principles` | WhatIfAnalyzer with default KB |
| `test_analyzer.py` | `test_whatif_custom_principles` | Custom principles override |
| `test_analyzer.py` | `test_analyzer_models_import` | Models importable from `analyzer.models` |
| `test_api.py` | `test_sops_endpoint` | GET /sops returns 9 SOPs |
| `test_api.py` | `test_sop_detail_modes` | GET /sops/9 has modes |
| `test_api.py` | `test_whatif_endpoint` | POST /analyze/whatif works |
| `test_api.py` | `test_historical_endpoint` | POST /analyze/historical works |

### Commands
```bash
python -m pytest tests/ -v
```

---

## Implementation Order

1. Extract analyzer models → `src/analyzer/models.py`
2. Fix SOP display in `decision_engine.py`
3. Fix SOP display in `app.js` + `style.css`
4. Add `KnowledgeBaseFactory` to `knowledge_base.py`
5. Create `WhatIfAnalyzer` in `src/analyzer/whatif_analyzer.py`
6. Update `src/analyzer/__init__.py` exports
7. Add new API endpoints to `api.py`
8. Add Historic Analyzer UI to `index.html` + `app.js` + `style.css`
9. Update `.agent/knowledge/interfaces.md`
10. Add tests
11. Run full test suite
12. Manual verification
13. `/post-phase-commit`
