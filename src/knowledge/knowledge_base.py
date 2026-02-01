"""Knowledge Base - Central repository for values, principles, and SOPs.

This module provides the KnowledgeBase class which loads and manages
the complete principles framework from YAML data files.
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel

from src.domain.values import Value, ValueSet
from src.domain.principles import Principle, SubPrinciple, PrincipleCategory
from src.domain.sops import SOP, SOPStep, SOPTrigger, TriggerType


class KnowledgeBase(BaseModel):
    """Central repository for all domain objects.
    
    Loads values, principles, and SOPs from YAML files and provides
    query methods for retrieval.
    
    Attributes:
        data_path: Path to the data directory
        values: Loaded values
        principles: Loaded principles
        sops: Loaded SOPs
    """
    
    data_path: Path
    values: ValueSet = ValueSet()
    principles: list[Principle] = []
    sops: list[SOP] = []
    _loaded: bool = False
    
    model_config = {"arbitrary_types_allowed": True}
    
    def load(self) -> None:
        """Load all data from YAML files.
        
        Reads values.yaml, principles.yaml, and sops.yaml from the
        data directory and populates the internal collections.
        """
        self._load_values()
        self._load_principles()
        self._load_sops()
        self._loaded = True
    
    def _load_values(self) -> None:
        """Load values from values.yaml."""
        values_file = self.data_path / "values.yaml"
        if not values_file.exists():
            return
        
        with open(values_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        all_values = []
        
        # Load core values
        for v in data.get("core_values", []):
            all_values.append(Value(**v))
        
        # Load optional values
        for v in data.get("optional_values", []):
            all_values.append(Value(**v))
        
        self.values = ValueSet(values=all_values)
    
    def _load_principles(self) -> None:
        """Load principles from principles.yaml."""
        principles_file = self.data_path / "principles.yaml"
        if not principles_file.exists():
            return
        
        with open(principles_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        self.principles = []
        for p_data in data.get("principles", []):
            # Parse sub-principles
            sub_principles = []
            for sp in p_data.get("sub_principles", []):
                sub_principles.append(SubPrinciple(
                    id=sp["id"],
                    text=sp["text"],
                    sub_items=sp.get("sub_items", [])
                ))
            
            # Parse categories
            categories = [
                PrincipleCategory(c) for c in p_data.get("categories", [])
            ]
            
            principle = Principle(
                id=p_data["id"],
                title=p_data["title"],
                sub_principles=sub_principles,
                related_sop_ids=p_data.get("related_sop_ids", []),
                related_value_ids=p_data.get("related_value_ids", []),
                categories=categories,
                tags=p_data.get("tags", [])
            )
            self.principles.append(principle)
    
    def _load_sops(self) -> None:
        """Load SOPs from sops.yaml."""
        sops_file = self.data_path / "sops.yaml"
        if not sops_file.exists():
            return
        
        with open(sops_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        self.sops = []
        for s_data in data.get("sops", []):
            # Parse triggers
            triggers = []
            for t in s_data.get("triggers", []):
                triggers.append(SOPTrigger(
                    trigger_type=TriggerType(t["trigger_type"]),
                    condition=t["condition"],
                    keywords=t.get("keywords", [])
                ))
            
            # Parse steps
            steps = []
            for step in s_data.get("steps", []):
                steps.append(SOPStep(
                    number=step["number"],
                    instruction=step["instruction"],
                    is_optional=step.get("is_optional", False),
                    notes=step.get("notes")
                ))
            
            # Parse modes (for SOPs with multiple modes like SOP 9)
            modes = {}
            for mode_key, mode_data in s_data.get("modes", {}).items():
                mode_steps = []
                for step in mode_data.get("steps", []):
                    mode_steps.append(SOPStep(
                        number=step["number"],
                        instruction=step["instruction"],
                        is_optional=step.get("is_optional", False),
                        notes=step.get("notes")
                    ))
                modes[mode_key] = mode_steps
            
            sop = SOP(
                id=s_data["id"],
                name=s_data["name"],
                purpose=s_data["purpose"],
                related_principle_ids=s_data.get("related_principle_ids", []),
                triggers=triggers,
                steps=steps,
                modes=modes
            )
            self.sops.append(sop)
    
    # Query methods
    
    def get_value(self, value_id: str) -> Optional[Value]:
        """Get a value by ID.
        
        Args:
            value_id: The unique identifier of the value.
            
        Returns:
            The Value if found, None otherwise.
        """
        return self.values.get_by_id(value_id)
    
    def get_principle(self, principle_id: int) -> Optional[Principle]:
        """Get a principle by ID.
        
        Args:
            principle_id: The principle number (1-45).
            
        Returns:
            The Principle if found, None otherwise.
        """
        for p in self.principles:
            if p.id == principle_id:
                return p
        return None
    
    def get_principles_by_category(
        self, category: PrincipleCategory
    ) -> list[Principle]:
        """Get all principles in a category.
        
        Args:
            category: The category to filter by.
            
        Returns:
            List of principles in that category.
        """
        return [p for p in self.principles if p.is_in_category(category)]
    
    def get_principles_by_tags(self, tags: list[str]) -> list[Principle]:
        """Get principles matching any of the given tags.
        
        Args:
            tags: List of tags to match.
            
        Returns:
            List of principles matching at least one tag.
        """
        matching = []
        for p in self.principles:
            if any(p.has_tag(tag) for tag in tags):
                matching.append(p)
        return matching
    
    def get_sop(self, sop_id: int) -> Optional[SOP]:
        """Get an SOP by ID.
        
        Args:
            sop_id: The SOP number (1-9).
            
        Returns:
            The SOP if found, None otherwise.
        """
        for s in self.sops:
            if s.id == sop_id:
                return s
        return None
    
    def get_sops_for_situation(self, situation_text: str) -> list[SOP]:
        """Get SOPs that should trigger for a situation.
        
        Args:
            situation_text: Description of the situation.
            
        Returns:
            List of SOPs that should be triggered.
        """
        return [s for s in self.sops if s.check_triggers(situation_text)]
    
    def get_related_principles(self, principle_id: int) -> list[Principle]:
        """Get principles related to a given principle.
        
        Finds principles that share SOPs, values, or categories.
        
        Args:
            principle_id: The principle to find relations for.
            
        Returns:
            List of related principles (excluding the input).
        """
        source = self.get_principle(principle_id)
        if not source:
            return []
        
        related = set()
        
        # Find by shared SOPs
        for p in self.principles:
            if p.id == principle_id:
                continue
            if any(s in source.related_sop_ids for s in p.related_sop_ids):
                related.add(p)
        
        # Find by shared categories
        for p in self.principles:
            if p.id == principle_id:
                continue
            if any(c in source.categories for c in p.categories):
                related.add(p)
        
        return list(related)
    
    def search_principles(self, query: str) -> list[Principle]:
        """Search principles by keyword in title or tags.
        
        Args:
            query: Search query (case-insensitive).
            
        Returns:
            List of matching principles.
        """
        query_lower = query.lower()
        matching = []
        for p in self.principles:
            if query_lower in p.title.lower():
                matching.append(p)
            elif any(query_lower in tag.lower() for tag in p.tags):
                matching.append(p)
        return matching
