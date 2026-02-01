"""Principle domain models.

Principles are actionable guidelines derived from values. They represent
the 'how' of decision-making and form the core of the decision framework.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class PrincipleCategory(str, Enum):
    """Categories for grouping related principles."""
    
    SELF_MANAGEMENT = "self_management"
    COMMUNICATION = "communication"
    DECISION_MAKING = "decision_making"
    RELATIONSHIPS = "relationships"
    PROFESSIONAL = "professional"
    GROWTH_LEARNING = "growth_learning"
    FINANCIAL = "financial"
    HEALTH_WELLBEING = "health_wellbeing"
    FAMILY = "family"


class SubPrinciple(BaseModel):
    """A sub-point within a principle.
    
    Sub-principles provide specific, actionable guidance within
    the broader principle.
    
    Attributes:
        id: Sub-principle identifier (e.g., 'a', 'b', 'c')
        text: The content of the sub-principle
        sub_items: Nested sub-items (e.g., 'i', 'ii')
    """
    
    id: str = Field(..., description="Sub-principle identifier (a, b, c, etc.)")
    text: str = Field(..., description="Content of the sub-principle")
    sub_items: list[str] = Field(default_factory=list, description="Nested sub-items")
    
    def __str__(self) -> str:
        return f"{self.id}. {self.text}"


class Principle(BaseModel):
    """A principle that guides decision-making.
    
    Principles are the core rules derived from values. Each principle
    has a title, optional sub-principles, and metadata for matching
    and categorization.
    
    Attributes:
        id: Sequential number (1-45)
        title: Short descriptive name
        sub_principles: Lettered sub-points with specific guidance
        related_sop_ids: IDs of related SOPs
        related_value_ids: IDs of values this principle supports
        categories: Categories this principle belongs to
        tags: Keywords for search and matching
    """
    
    id: int = Field(..., ge=1, description="Principle number")
    title: str = Field(..., min_length=1, description="Principle title")
    sub_principles: list[SubPrinciple] = Field(
        default_factory=list, 
        description="Sub-points within the principle"
    )
    related_sop_ids: list[int] = Field(
        default_factory=list, 
        description="IDs of related SOPs"
    )
    related_value_ids: list[str] = Field(
        default_factory=list, 
        description="IDs of values this principle supports"
    )
    categories: list[PrincipleCategory] = Field(
        default_factory=list, 
        description="Categories this principle belongs to"
    )
    tags: list[str] = Field(
        default_factory=list, 
        description="Keywords for matching"
    )
    
    def get_full_text(self) -> str:
        """Get the complete principle text including sub-principles.
        
        Returns:
            Full text representation of the principle.
        """
        lines = [f"{self.id}. {self.title}"]
        for sub in self.sub_principles:
            lines.append(f"   {sub.id}. {sub.text}")
            for i, item in enumerate(sub.sub_items):
                lines.append(f"      {chr(105 + i)}. {item}")  # i, ii, iii...
        return "\n".join(lines)
    
    def has_tag(self, tag: str) -> bool:
        """Check if principle has a specific tag.
        
        Args:
            tag: The tag to check for (case-insensitive).
            
        Returns:
            True if the principle has this tag.
        """
        return tag.lower() in [t.lower() for t in self.tags]
    
    def is_in_category(self, category: PrincipleCategory) -> bool:
        """Check if principle belongs to a category.
        
        Args:
            category: The category to check.
            
        Returns:
            True if the principle is in this category.
        """
        return category in self.categories
    
    def __str__(self) -> str:
        return f"Principle {self.id}: {self.title}"
    
    def __hash__(self) -> int:
        return hash(self.id)


class PrincipleRelationship(BaseModel):
    """A relationship between two principles.
    
    Tracks how principles relate to each other - whether they
    reinforce, complement, or potentially conflict.
    
    Attributes:
        principle_id_1: First principle ID
        principle_id_2: Second principle ID
        relationship_type: Type of relationship
        description: Explanation of the relationship
    """
    
    class RelationshipType(str, Enum):
        REINFORCES = "reinforces"  # Both point same direction
        COMPLEMENTS = "complements"  # Work together
        TENSIONS = "tensions"  # May conflict in some situations
        PREREQUISITE = "prerequisite"  # One requires the other first
    
    principle_id_1: int = Field(..., description="First principle ID")
    principle_id_2: int = Field(..., description="Second principle ID")
    relationship_type: RelationshipType = Field(..., description="Type of relationship")
    description: Optional[str] = Field(None, description="Explanation of relationship")
