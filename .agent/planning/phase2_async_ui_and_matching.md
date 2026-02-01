# Phase 2: Async UI, LLM Fallback Visibility, and Matching Improvements

**Status:** Ready for Implementation  
**Prerequisites:** Phase 1 Complete (Core system working)

---

## Problem Statement

Testing revealed that realistic situations like *"Stepbrother demanding more than his share of land"* return generic results due to:
1. Semantic matching silently fails without clear feedback
2. Keyword matching too narrow (e.g., "share" triggers wrong SOP)
3. UI blocks during API calls with no progress indication
4. No visibility into which matching strategy succeeded/failed

---

## Proposed Changes

### 1. Async UI with Status Indicators

#### [MODIFY] `src/interfaces/api.py`
- Add `/analyze/stream` endpoint returning Server-Sent Events (SSE)
- Emit status events: `matching_started`, `semantic_done`, `keyword_done`, `complete`
- Include `matching_method_used` in response (semantic/keyword/hybrid)

#### [MODIFY] `src/interfaces/static/app.js`
- Use `EventSource` for SSE connection
- Show animated status indicator: "Analyzing... → Semantic matching... → Complete"
- Display which LLM was used (Gemini/DeepSeek/Heuristic fallback)

#### [MODIFY] `src/interfaces/static/index.html`
- Add status badge component
- Add "Method Used" display section

---

### 2. LLM Fallback Visibility

#### [MODIFY] `src/engine/decision_engine.py`
- Return metadata: `{"matching_methods": ["semantic", "keyword"], "semantic_success": true/false}`
- Log which strategy contributed to final matches

#### [MODIFY] `src/engine/models.py`
Add to `DecisionResult`:
```python
matching_metadata: Optional[MatchingMetadata] = None

class MatchingMetadata(BaseModel):
    strategies_attempted: list[str]  # ["semantic", "keyword"]
    strategies_succeeded: list[str]  # ["keyword"]
    llm_provider_used: Optional[str]  # "gemini" | "deepseek" | None
    fallback_triggered: bool
```

#### [MODIFY] `src/engine/embeddings.py`
- Add DeepSeek embedding fallback
- Return structured error info instead of print statements

---

### 3. Enhanced Logging/Debugging

The `.env.example` file already exists with the required API key templates.

---

## Verification Plan

### Automated Tests
```bash
pytest tests/test_api.py::test_analyze_stream -v
pytest tests/test_engine.py::test_matching_metadata -v
```

### Manual Verification
1. Run API: `python -m src.interfaces.api`
2. Submit: "Stepbrother demanding land share with historical grievances"
3. Verify: Status indicator shows progress
4. Verify: "Method Used: Semantic + Keyword" appears in result
5. Verify: Principles 14, 39, 43 match

### API Key Test Matrix
| Gemini Key | DeepSeek Key | Expected Behavior |
|------------|--------------|-------------------|
| ✅ Valid | ✅ Valid | Use Gemini, DeepSeek unused |
| ✅ Valid | ❌ Invalid | Use Gemini |
| ❌ Invalid | ✅ Valid | Fallback to DeepSeek |
| ❌ Invalid | ❌ Invalid | Fallback to keyword heuristics |

---

## Implementation Order

1. **Update models.py** - Add `MatchingMetadata`
2. **Update decision_engine.py** - Capture and return metadata
3. **Update embeddings.py** - Add DeepSeek fallback
4. **Update api.py** - Add SSE streaming endpoint
5. **Update frontend** - Async status + metadata display
6. **Add tests** - Cover new metadata and streaming

---

## Out of Scope (Future Phases)

- Expanding principle/SOP tags (preserve original data)
- Advanced semantic caching
- Custom embedding fine-tuning
