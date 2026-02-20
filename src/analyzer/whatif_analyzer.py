"""What-If Analyzer - Analyze situations with custom principles.

This module provides the WhatIfAnalyzer service which allows users to
simulate decision outcomes by applying a custom set of principles
(or the standard set) to a situation.
"""

from typing import Optional, List

from src.domain.principles import Principle
from src.domain.values import ValueSet
from src.domain.sops import SOP
from src.domain.situations import Situation
from src.engine.decision_engine import DecisionEngine
from src.engine.models import DecisionResult
from src.knowledge.knowledge_base import KnowledgeBaseFactory


class WhatIfAnalyzer:
    """Analyzes situations using custom or standard principles.
    
    Allows injecting a modified set of principles to see how the
    recommendation changes (Simulation/What-If).
    """
    
    def __init__(self, default_engine: DecisionEngine):
        """Initialize with the default decision engine.
        
        Args:
            default_engine: The standard decision engine (used as base).
        """
        self.default_engine = default_engine
    
    def analyze(
        self, 
        situation: Situation, 
        custom_principles: Optional[List[Principle]] = None
    ) -> DecisionResult:
        """Analyze a situation, optionally overriding principles.
        
        Args:
            situation: The situation to analyze.
            custom_principles: Optional list of principles to use instead of the default.
            
        Returns:
            DecisionResult based on the provided (or default) principles.
        """
        if not custom_principles:
            # fast path: use default engine
            return self.default_engine.evaluate(situation)
            
        # Create a temporary KB with custom principles
        # We preserve the default values and SOPs from the main engine's KB
        default_kb = self.default_engine.kb
        
        temp_kb = KnowledgeBaseFactory.create_from_objects(
            principles=custom_principles,
            sops=default_kb.sops,
            values=default_kb.values
        )
        
        # Create a new engine instance with this temporary KB
        # Note: We create a fresh engine to avoid side effects, 
        # but matching strategies (like semantic) might need re-init
        # or sharing. For now, we'll instantiate a new DecisionEngine.
        # Optimization: We could share the embedding service if we can pass it 
        # or if it's a singleton.
        
        temp_engine = DecisionEngine(knowledge_base=temp_kb)
        
        # Should we manually share the embedding service to avoid reloading models?
        # DecisionEngine inits its own MatchingStrategy.
        # If EmbeddingService is heavy, this is slow.
        # We can assign the existing strategy if compatible.
        
        # Optimization: share strategies
        if hasattr(self.default_engine, 'semantic_strategy'):
            temp_engine.semantic_strategy = self.default_engine.semantic_strategy
        if hasattr(self.default_engine, 'keyword_strategy'):
            temp_engine.keyword_strategy = self.default_engine.keyword_strategy
            
        return temp_engine.evaluate(situation)
