# Knowledge Base Internals

## Purpose

The Knowledge Base is responsible for:
1. Loading values, principles, and SOPs from YAML files
2. Providing efficient query methods for retrieval
3. Managing relationships between entities
4. Future: semantic indexing for intelligent matching

## Key Classes

### `KnowledgeBase`
The central repository for all domain objects.

```python
class KnowledgeBase:
    def __init__(self, data_path: Path)
    def load(self) -> None
    def get_value(self, value_id: str) -> Value
    def get_principle(self, principle_id: int) -> Principle
    def get_principles_by_tags(self, tags: List[str]) -> List[Principle]
    def get_sop(self, sop_id: int) -> SOP
    def get_sop_for_trigger(self, trigger_type: str) -> Optional[SOP]
    def get_related_principles(self, principle_id: int) -> List[Principle]
```

### `PrincipleIndexer`
Handles indexing for fast retrieval.

```python
class PrincipleIndexer:
    def build_index(self, principles: List[Principle]) -> None
    def search_by_keyword(self, keyword: str) -> List[Principle]
    def search_by_tags(self, tags: List[str]) -> List[Principle]
```

## Data Loading

YAML files are loaded on initialization:

```python
kb = KnowledgeBase(Path("data/"))
kb.load()  # Loads values.yaml, principles.yaml, sops.yaml
```

## Query Patterns

### By ID
```python
principle = kb.get_principle(14)  # "Separate Emotion from High-Stakes Decisions"
```

### By Tag
```python
communication_principles = kb.get_principles_by_tags(["communication", "transparency"])
```

### By Relationship
```python
related = kb.get_related_principles(4)  # Principles related to "Calibrated Transparency"
```

## Extension Points

- **Custom Indexers**: Implement `IndexerStrategy` for different indexing approaches
- **Caching**: Add caching layer for frequently accessed principles
- **Semantic Search**: Add vector embeddings for meaning-based matching
