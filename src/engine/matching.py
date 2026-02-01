"""Matching strategies for finding applicable principles.

This module defines the Strategy pattern for principle matching, allowing
different algorithms to be plugged into the Decision Engine.
"""

from abc import ABC, abstractmethod
from typing import List

import math
from abc import ABC, abstractmethod
from typing import List

from src.domain.principles import Principle
from src.domain.situations import Situation
from src.engine.models import PrincipleMatch
from src.engine.embeddings import EmbeddingService


class MatchingStrategy(ABC):
    """Abstract base class for principle matching strategies."""

    @abstractmethod
    def match(
        self, situation: Situation, principles: List[Principle]
    ) -> List[PrincipleMatch]:
        """Match a situation against a list of principles.

        Args:
            situation: The situation to analyze.
            principles: The available principles to match against.

        Returns:
            List of matches with relevance scores.
        """
        pass


class KeywordMatchingStrategy(MatchingStrategy):
    """Matches principles based on shared tags and keywords.

    This strategy:
    1. Checks for exact tag matches in the situation description/context.
    2. Checks if principle title words appear in the situation.
    3. Calculates a score based on match density and explicit weighting.
    """

    def match(
        self, situation: Situation, principles: List[Principle]
    ) -> List[PrincipleMatch]:
        """Match using keyword and tag overlap."""
        matches = []
        
        # Prepare situation text for searching
        situation_text = situation.get_full_description().lower()
        situation_words = set(situation_text.split())

        for principle in principles:
            match_reasons = []
            score_accum = 0.0

            # 1. Tag Matching (High weight)
            matched_tags = [
                tag for tag in principle.tags 
                if tag.lower() in situation_text
            ]
            if matched_tags:
                count = len(matched_tags)
                # Diminishing returns for multiple tags
                tag_score = min(0.6 + (count * 0.1), 0.9)
                score_accum += tag_score
                match_reasons.append(f"Tags: {', '.join(matched_tags)}")

            # 2. Title Keyword Matching (Medium weight)
            # Filter out common words (stop words) - rudimentary list
            stop_words = {"the", "and", "or", "a", "an", "to", "of", "in", "for", "with"}
            title_words = [
                w.lower() for w in principle.title.split() 
                if w.lower() not in stop_words and len(w) > 3
            ]
            
            matched_keywords = [
                w for w in title_words if w in situation_text
            ]
            
            if matched_keywords:
                # Only add if we haven't already maxed out score significantly
                keyword_score = min(len(matched_keywords) * 0.15, 0.5)
                # If we have tags, keywords add less value
                if matched_tags:
                    score_accum += keyword_score * 0.5
                else:
                    score_accum += keyword_score
                match_reasons.append(f"Keywords: {', '.join(matched_keywords)}")

            # Finalize score
            if score_accum > 0:
                final_score = min(score_accum, 1.0)
                matches.append(PrincipleMatch(
                    principle=principle,
                    relevance_score=final_score,
                    match_reason="; ".join(match_reasons)
                ))

        # Sort by score descending
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches


class SemanticMatchingStrategy(MatchingStrategy):
    """Matches principles using vector semantic similarity."""
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.principle_embeddings = {}
        
    def _run_embedding_setup(self, principles: List[Principle]):
        """Embed all principles if not done yet."""
        if self.principle_embeddings:
            return
            
        # print("DEBUG: Generating embeddings for principles...")
        for p in principles:
            # Create a rich representation of the principle
            # Title is most important, but tags help context
            text = f"{p.title}. Keywords: {', '.join(p.tags)}"
            vec = self.embedding_service.embed_text(text)
            if vec:
                self.principle_embeddings[p.id] = vec
                
    def match(self, situation: Situation, principles: List[Principle]) -> List[PrincipleMatch]:
        """Match using cosine similarity."""
        # 1. Ensure principles are embedded
        self._run_embedding_setup(principles)
        if not self.principle_embeddings:
            print("Warning: No principle embeddings available.")
            return []
            
        # 2. Embed situation
        sit_vec = self.embedding_service.embed_text(situation.description)
        if not sit_vec:
            print("Warning: Could not embed situation.")
            return []
            
        matches = []
        for p in principles:
            if p.id not in self.principle_embeddings:
                continue
                
            p_vec = self.principle_embeddings[p.id]
            score = self._cosine_similarity(sit_vec, p_vec)
            
            # Threshold for semantic match
            # 0.7 is usually a good starting point for 'related'
            if score > 0.65:
                matches.append(PrincipleMatch(
                    principle=p,
                    relevance_score=score,
                    match_reason=f"Semantic similarity: {score:.2f}"
                ))
                
        matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return matches

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_a = math.sqrt(sum(a * a for a in v1))
        norm_b = math.sqrt(sum(b * b for b in v2))
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return dot_product / (norm_a * norm_b)
