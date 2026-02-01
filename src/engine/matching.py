"""Matching strategies for finding applicable principles.

This module defines the Strategy pattern for principle matching, allowing
different algorithms to be plugged into the Decision Engine.
"""

from abc import ABC, abstractmethod
from typing import List

from src.domain.principles import Principle
from src.domain.situations import Situation
from src.engine.models import PrincipleMatch


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

        # Sort by relevance
        matches.sort(key=lambda m: m.relevance_score, reverse=True)
        return matches
