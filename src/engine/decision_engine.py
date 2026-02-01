"""Decision Engine - Core logic for applying principles to situations.

This module contains the DecisionEngine class which orchestrates
the matching of situations to principles and generation of recommendations.
"""

from typing import Optional, List

from src.domain.sops import SOP
from src.domain.situations import Situation
from src.knowledge.knowledge_base import KnowledgeBase
from src.engine.models import DecisionResult, PrincipleMatch, AlignmentScore
# Import the matching strategy interface and default implementation
from src.engine.matching import MatchingStrategy, KeywordMatchingStrategy, SemanticMatchingStrategy
from src.engine.embeddings import EmbeddingService


class DecisionEngine:
    """Orchestrates the decision-making process.
    
    Takes situations and applies the principles framework to generate
    recommendations using a configurable matching strategy.
    """
    
    def __init__(self, knowledge_base: KnowledgeBase):
        """Initialize the decision engine.
        
        Args:
            knowledge_base: The loaded knowledge base.
        """
        self.kb = knowledge_base
        # Initialize strategies
        self.keyword_strategy = KeywordMatchingStrategy()
        
        # Try to initialize semantic strategy
        self.embedding_service = EmbeddingService()
        self.semantic_strategy = SemanticMatchingStrategy(self.embedding_service)
        
    def evaluate(self, situation: Situation) -> DecisionResult:
        """Evaluate a situation against the principles framework.
        
        Args:
            situation: The situation to analyze.
            
        Returns:
            A DecisionResult with applicable principles and recommendations.
        """
        # 1. Match Principles
        # First try semantic matching
        matches = self.semantic_strategy.match(situation, self.kb.principles)
        
        # Fallback or Augment with Keyword matching
        # If semantic returned nothing or very few matches, run keyword
        keyword_matches = self.keyword_strategy.match(situation, self.kb.principles)
        
        # Combine matches (simple logic: union by ID, take higher score)
        combined_map = {}
        for m in matches:
            combined_map[m.principle.id] = m
            
        for m in keyword_matches:
            if m.principle.id in combined_map:
                # If existing score is lower, update?? Usually semantic is better but maybe not.
                # Let's keep the max score
                existing = combined_map[m.principle.id]
                if m.relevance_score > existing.relevance_score:
                    combined_map[m.principle.id] = m
            else:
                combined_map[m.principle.id] = m
        
        final_matches = list(combined_map.values())
        final_matches.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Take top 3
        applicable = final_matches[:3]
        
        # Prepare Metadata
        strategies_succeeded = []
        # Check which strategies contributed to final top 3 (heuristic check)
        # Note: Ideally we'd track source in PrincipleMatch
        strategies_attempted = ["semantic", "keyword"]
        
        from src.engine.models import MatchingMetadata
        
        # Assume Gemini for now as we don't have return signal from embedding service yet
        # Phase 2 improvement: make embedding service return metadata
        llm_provider = "gemini" 
        
        metadata = MatchingMetadata(
            strategies_attempted=strategies_attempted,
            strategies_succeeded=strategies_attempted, # simplified
            llm_provider_used=llm_provider,
            fallback_triggered=False
        )
        
        # 2. Get triggered SOPs
        triggered_sops = self.get_applicable_sops(situation)
        
        # 3. Calculate Value Alignment
        alignment = self._calculate_alignment(applicable)
        
        # 4. Generate Reasoning and Recommendation
        reasoning, recommendation = self._generate_reasoning(
            situation, applicable, triggered_sops, alignment
        )
        
        # 5. Calculate Confidence
        confidence = self._calculate_confidence(applicable, triggered_sops)
        
        return DecisionResult(
            situation=situation,
            applicable_principles=applicable,
            triggered_sops=triggered_sops,
            recommendation=recommendation,
            value_alignment=alignment,
            confidence=confidence,
            reasoning=reasoning,
            matching_metadata=metadata
        )
    
    def get_applicable_principles(
        self, situation: Situation
    ) -> list[PrincipleMatch]:
        """Find principles that apply to a situation.
        
        Args:
            situation: The situation to match against.
            
        Returns:
            List of matched principles with scores.
        """
        return self.matcher.match(situation, self.kb.principles)
    
    def get_applicable_sops(self, situation: Situation) -> list[SOP]:
        """Find SOPs that should trigger for a situation.
        
        Args:
            situation: The situation to check triggers against.
            
        Returns:
            List of triggered SOPs.
        """
        situation_text = situation.get_full_description()
        return self.kb.get_sops_for_situation(situation_text)

    def _calculate_alignment(self, matches: List[PrincipleMatch]) -> AlignmentScore:
        """Calculate alignment with core values based on matched principles.
        
        Args:
            matches: The matched principles.
            
        Returns:
            AlignmentScore object.
        """
        if not matches:
            return AlignmentScore(overall_score=0.0)
            
        value_scores = {}
        total_weight = 0.0
        
        for match in matches:
            # Each principle adds to the score of its related values
            weight = match.relevance_score
            for val_id in match.principle.related_value_ids:
                value_scores[val_id] = value_scores.get(val_id, 0.0) + weight
                total_weight += weight
                
        # Normalize scores roughly 0-1 (heuristic)
        # If total_weight is high, it means many relevant principles align with values
        overall = min(total_weight / 3.0, 1.0) if total_weight > 0 else 0.0
        
        return AlignmentScore(
            overall_score=overall,
            value_scores=value_scores
        )

    def _generate_reasoning(
        self, 
        situation: Situation, 
        matches: List[PrincipleMatch], 
        sops: List[SOP],
        alignment: AlignmentScore
    ) -> tuple[str, str]:
        """Generate human-readable reasoning and recommendation.
        
        Args:
            situation: The analyzed situation.
            matches: Matched principles.
            sops: Triggered SOPs.
            alignment: Value alignment scores.
            
        Returns:
            Tuple of (reasoning_text, recommendation_text).
        """
        reasoning_parts = []
        rec_parts = []
        
        # Analyze Matches
        if matches:
            top_match = matches[0]
            reasoning_parts.append(
                f"The primary principle identified is '{top_match.principle.title}' "
                f"(Relevance: {top_match.relevance_score:.2f})."
            )
            
            # Add context for top 3 matches
            for i, match in enumerate(matches[:3]):
                p = match.principle
                rec_parts.append(f"{i+1}. **Apply Principle {p.id}:** {p.title}")
                # Include the first sub-principle as specific advice
                if p.sub_principles:
                    rec_parts.append(f"   - Guidance: {p.sub_principles[0].text}")
        else:
            reasoning_parts.append("No specific principles matched the situation keywords strongly.")
            rec_parts.append("Review the situation description and add more specific keywords or context.")

        # Analyze SOPs
        if sops:
            sop_names = [s.name for s in sops]
            reasoning_parts.append(
                f"The situation triggers the following Standard Operating Procedures: {', '.join(sop_names)}."
            )
            rec_parts.append(f"**IMMEDIATE ACTION:** Execute SOP(s): {', '.join(sop_names)}.")

        # Analyze Values
        if alignment.value_scores:
            top_values = sorted(
                alignment.value_scores.items(), key=lambda x: x[1], reverse=True
            )[:2]
            val_names = [v[0] for v in top_values]
            reasoning_parts.append(
                f"This course of action strongly aligns with your values of {', '.join(val_names)}."
            )

        reasoning = " ".join(reasoning_parts)
        recommendation = "\n".join(rec_parts)
        
        return reasoning, recommendation

    def _calculate_confidence(
        self, matches: List[PrincipleMatch], sops: List[SOP]
    ) -> float:
        """Calculate confidence score for the recommendation.
        
        Args:
            matches: Matched principles.
            sops: Triggered SOPs.
            
        Returns:
            Confidence score 0-1.
        """
        if not matches and not sops:
            return 0.1
            
        # Base confidence on the best match
        base = matches[0].relevance_score if matches else 0.0
        
        # Boost confidence if SOPs are triggered (SOPs are specific and high-confidence)
        if sops:
            base = max(base, 0.8)
        else:
            # If multiple matches verify each other, boost slightly
            if len(matches) > 1:
                base = min(base + 0.1, 1.0)
                
        return round(base, 2)
