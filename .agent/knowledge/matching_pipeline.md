# Matching Pipeline - Technical Details

## Overview

The Decision Engine uses a **hybrid matching approach** combining semantic (LLM-based) and keyword strategies.

## Pipeline Flow

```
┌─────────────────┐
│   Situation     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     SemanticMatchingStrategy            │
│  (Gemini embeddings → cosine similarity)│
└────────┬────────────────────────────────┘
         │ Returns matches (may be empty)
         ▼
┌─────────────────────────────────────────┐
│     KeywordMatchingStrategy             │
│  (Tag + title word matching)            │
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│     Combine & Deduplicate               │
│  (Union by principle ID, keep max score)│
└────────┬────────────────────────────────┘
         │
         ▼
┌─────────────────┐
│  Top 3 Matches  │
└─────────────────┘
```

## Strategy Details

### Semantic Matching
- Uses `text-embedding-004` model
- Embeds: `"{principle.title}. Keywords: {tags}"`
- Similarity threshold: **0.65** (configurable)
- Caches embeddings for performance

### Keyword Matching
- **Tag match weight**: 0.6 base + 0.1 per additional (max 0.9)
- **Title keyword weight**: 0.15 per word (max 0.5)
- Stop words filtered: the, and, or, a, an, to, of, in, for, with

## Common Failure Modes

| Symptom | Cause | Solution |
|---------|-------|----------|
| No matches | API key missing/invalid | Check `.env` configuration |
| Wrong matches | "share" in text triggers SOP 3 | Semantic matching should override |
| Generic results | Low semantic scores | Verify embeddings are returning vectors |

## Debugging

Check semantic strategy:
```python
engine.semantic_strategy.principle_embeddings  # Should have 45 entries
```

Check keyword matches:
```python
engine.keyword_strategy.match(situation, kb.principles)
```
