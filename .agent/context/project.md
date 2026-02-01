# Project Context - Principles-Based Decision System

## Purpose

This system transforms personal values, principles, and Standard Operating Procedures (SOPs) into an actionable decision-support tool. It enables:

1. **Situation Analysis** - Given a scenario, identify which principles apply
2. **Decision Recommendation** - Suggest actions aligned with the user's value system
3. **Historical Review** - Analyze past decisions against current principles
4. **Pattern Detection** - Identify recurring decision patterns and gaps

## Architecture Overview

The system follows a **modular, layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                   Interface Layer                        │
│              (CLI, API, Web Dashboard)                  │
├─────────────────────────────────────────────────────────┤
│                 Application Services                     │
│    (Decision Engine, Historical Analyzer, Reporting)    │
├─────────────────────────────────────────────────────────┤
│                    Core Domain                          │
│        (Values, Principles, SOPs, Situations)           │
├─────────────────────────────────────────────────────────┤
│                   Infrastructure                         │
│        (Knowledge Base, Repository, Config)             │
└─────────────────────────────────────────────────────────┘
```

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Python 3.10+ | Modern features, good ecosystem, AI integration ready |
| Pydantic models | Strong typing, validation, serialization |
| YAML for data | Human-readable, easy to edit principles directly |
| Modular subsystems | Can build/test independently |
| Strategy pattern | Swappable matching/evaluation algorithms |

## Subsystems (Modules)

1. **`src/domain/`** - Core domain models (Value, Principle, SOP, Situation)
2. **`src/knowledge/`** - Knowledge base for loading/querying principles
3. **`src/engine/`** - Decision engine that matches principles to situations
4. **`src/analyzer/`** - Historical analysis and pattern detection
5. **`src/reporting/`** - Report generation (Markdown, HTML)
6. **`src/interfaces/`** - CLI and API entry points

## Data Files

- `data/values.yaml` - Core values (Justice, Contribution, Family, Generosity)
- `data/principles.yaml` - All 45 principles with sub-points
- `data/sops.yaml` - 9 Standard Operating Procedures
- `data/historical_situations/` - Past situations for analysis

## Dependencies

Core: `pyyaml`, `pydantic`, `typer`, `rich`, `jinja2`
Optional: `fastapi`, `uvicorn` (for API)

## File Naming Conventions

- Modules: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
