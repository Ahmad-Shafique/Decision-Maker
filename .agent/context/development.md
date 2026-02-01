# Development Standards

## Coding Conventions

### Python Style
- **Formatter**: Black (line length 100)
- **Linter**: Ruff
- **Type Checker**: MyPy (strict mode)
- **Python Version**: 3.10+

### Naming
```python
# Classes: PascalCase
class DecisionEngine:
    pass

# Functions/Methods: snake_case
def evaluate_situation(situation: Situation) -> DecisionResult:
    pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_CONFIDENCE_THRESHOLD = 0.7

# Private: leading underscore
def _internal_helper():
    pass
```

### Imports
```python
# Standard library
from typing import Optional, List
from dataclasses import dataclass
from enum import Enum

# Third-party
from pydantic import BaseModel
import yaml

# Local
from src.domain.values import Value
from src.domain.principles import Principle
```

## Design Patterns in Use

### Domain Models
Use **Pydantic BaseModel** for all domain objects:
```python
from pydantic import BaseModel, Field

class Value(BaseModel):
    id: str
    name: str
    description: str
    priority: int = Field(ge=1, le=10)
```

### Repository Pattern
Abstract data access behind repository interfaces:
```python
from abc import ABC, abstractmethod

class PrincipleRepository(ABC):
    @abstractmethod
    def get_by_id(self, principle_id: int) -> Principle:
        pass
    
    @abstractmethod
    def get_by_tags(self, tags: List[str]) -> List[Principle]:
        pass
```

### Strategy Pattern
For swappable algorithms:
```python
class MatchingStrategy(ABC):
    @abstractmethod
    def match(self, situation: Situation, principles: List[Principle]) -> List[Match]:
        pass

class KeywordMatcher(MatchingStrategy):
    def match(self, situation, principles):
        # Keyword-based matching
        pass

class SemanticMatcher(MatchingStrategy):
    def match(self, situation, principles):
        # Embedding-based semantic matching
        pass
```

## File Organization

### Module Structure
Each subsystem module should have:
```
src/subsystem/
├── __init__.py      # Public exports
├── models.py        # Data models (if needed beyond domain)
├── service.py       # Main service class
├── repository.py    # Data access (if needed)
└── exceptions.py    # Custom exceptions
```

### Test Structure
Mirror the source structure:
```
tests/
├── test_domain/
│   ├── test_values.py
│   └── test_principles.py
├── test_engine/
│   └── test_decision_engine.py
└── conftest.py      # Shared fixtures
```

## Documentation

### Docstrings
Use Google-style docstrings:
```python
def evaluate_situation(self, situation: Situation) -> DecisionResult:
    """Evaluate a situation against the principles framework.
    
    Args:
        situation: The situation to analyze.
        
    Returns:
        A DecisionResult with applicable principles and recommendations.
        
    Raises:
        InvalidSituationError: If situation is malformed.
    """
    pass
```

### Module Docstrings
Every module should have a top-level docstring:
```python
"""Decision Engine - Core logic for applying principles to situations.

This module contains the DecisionEngine class which orchestrates
the matching of situations to principles and generation of recommendations.
"""
```

## Testing

### Test Naming
```python
def test_value_creation_with_valid_data():
    pass

def test_principle_matching_returns_empty_for_no_matches():
    pass

def test_sop_triggers_on_high_stakes_financial_decision():
    pass
```

### Fixtures
Use pytest fixtures for common test data:
```python
@pytest.fixture
def sample_values():
    return [
        Value(id="justice", name="Justice", description="Being ethically good", priority=1),
        # ...
    ]
```

## Error Handling

### Custom Exceptions
Define in `src/core/exceptions.py`:
```python
class DecisionSystemError(Exception):
    """Base exception for the decision system."""
    pass

class PrincipleNotFoundError(DecisionSystemError):
    """Raised when a principle cannot be found."""
    pass

class InvalidSituationError(DecisionSystemError):
    """Raised when a situation is malformed."""
    pass
```

## Commit Messages
Use conventional commits:
- `feat: add principle matching algorithm`
- `fix: correct SOP trigger logic`
- `docs: update domain context`
- `refactor: extract matching into strategy`
- `test: add tests for historical analyzer`
