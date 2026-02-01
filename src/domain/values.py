"""Value domain models.

Values represent the fundamental beliefs that guide all decisions.
They are the 'why' behind actions and form the foundation of the
principles framework.
"""

from typing import Optional
from pydantic import BaseModel, Field


class Value(BaseModel):
    """A core value that guides decision-making.
    
    Values are immutable during system operation and represent
    fundamental beliefs. The priority determines their weight
    when principles conflict.
    
    Attributes:
        id: Unique identifier (e.g., 'justice', 'contribution')
        name: Display name of the value
        description: Detailed explanation of what this value means
        priority: Priority rank (1 = highest priority)
        is_core: Whether this is a core value or optional
    """
    
    id: str = Field(..., min_length=1, description="Unique identifier for the value")
    name: str = Field(..., min_length=1, description="Display name")
    description: str = Field(..., description="What this value means")
    priority: int = Field(..., ge=1, le=100, description="Priority rank (1 = highest)")
    is_core: bool = Field(default=True, description="Whether this is a core value")
    
    def __str__(self) -> str:
        return f"{self.name} (Priority: {self.priority})"
    
    def __hash__(self) -> int:
        return hash(self.id)


class ValueSet(BaseModel):
    """A collection of values forming a complete value system.
    
    Manages the full set of values, providing access by ID and
    maintaining priority ordering.
    
    Attributes:
        values: List of all values in the system
    """
    
    values: list[Value] = Field(default_factory=list)
    
    def get_by_id(self, value_id: str) -> Optional[Value]:
        """Get a value by its ID.
        
        Args:
            value_id: The unique identifier of the value.
            
        Returns:
            The Value if found, None otherwise.
        """
        for value in self.values:
            if value.id == value_id:
                return value
        return None
    
    def get_core_values(self) -> list[Value]:
        """Get all core values, sorted by priority.
        
        Returns:
            List of core values sorted by priority (highest first).
        """
        return sorted(
            [v for v in self.values if v.is_core],
            key=lambda v: v.priority
        )
    
    def get_optional_values(self) -> list[Value]:
        """Get all optional values.
        
        Returns:
            List of optional values.
        """
        return [v for v in self.values if not v.is_core]
    
    def add_value(self, value: Value) -> None:
        """Add a value to the set.
        
        Args:
            value: The value to add.
            
        Raises:
            ValueError: If a value with this ID already exists.
        """
        if self.get_by_id(value.id):
            raise ValueError(f"Value with ID '{value.id}' already exists")
        self.values.append(value)
    
    def __len__(self) -> int:
        return len(self.values)
    
    def __iter__(self):
        return iter(sorted(self.values, key=lambda v: v.priority))
