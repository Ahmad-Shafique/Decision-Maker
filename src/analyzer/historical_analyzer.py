"""Historical Analyzer - Retrospective analysis of past decisions.

This module enables analysis of historical situations to understand
what the principles framework would have recommended. It uses a prioritized
LLM strategy (Gemini -> DeepSeek) with a heuristic fallback.
"""

import os
import json
import requests
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from src.domain.situations import HistoricalSituation
from src.engine.models import DecisionResult
# Note: DecisionEngine is imported only for type hinting if needed
from src.engine.decision_engine import DecisionEngine

# Load environment variables
load_dotenv()


class Gap(BaseModel):
    """A gap between actual and recommended decision.
    
    Attributes:
        gap_type: Type of gap (missed_principle, wrong_priority, etc.)
        description: Details about the gap
        severity: How significant the gap is (1-10)
    """
    
    gap_type: str
    description: str
    severity: int = Field(ge=1, le=10)


class Lesson(BaseModel):
    """A lesson learned from the analysis.
    
    Attributes:
        principle_id: Related principle (if any)
        insight: The lesson learned
        actionable: Specific action to take
    """
    
    principle_id: Optional[int] = None
    insight: str
    actionable: str


class AnalysisReport(BaseModel):
    """Complete analysis of a historical situation.
    
    Attributes:
        situation: The historical situation analyzed
        actual_decision: What was actually decided
        actual_outcome: What happened as a result
        recommended_decision: What principles would have said
        gaps: Differences between actual and recommended
        lessons: Lessons learned
        principle_adherence_score: How well principles were followed (0-1)
    """
    
    situation: HistoricalSituation
    actual_decision: str
    actual_outcome: str
    recommended_decision: DecisionResult
    gaps: list[Gap] = Field(default_factory=list)
    lessons: list[Lesson] = Field(default_factory=list)
    principle_adherence_score: float = Field(ge=0, le=1)


class HistoricalAnalyzer:
    """Analyzes past decisions against the principles framework.
    
    Uses LLMs (Gemini, then DeepSeek) to semantically analyze gaps,
    falling back to keyword heuristics if LLMs are unavailable.
    """
    
    def __init__(self, decision_engine: DecisionEngine):
        """Initialize the analyzer.
        
        Args:
            decision_engine: The decision engine to use for recommendations.
        """
        self.engine = decision_engine
    
    def analyze(self, historical: HistoricalSituation) -> AnalysisReport:
        """Analyze a historical situation.
        
        Args:
            historical: The past situation with actual outcome.
            
        Returns:
            Complete analysis report.
        """
        # 1. Get what principles would have recommended
        recommended = self.what_would_principles_say(historical)
        
        # 2. Analyze differences using prioritized strategy
        try:
            gaps, lessons = self._analyze_with_gemini(historical, recommended)
        except Exception as e_gemini:
            # print(f"Gemini analysis failed: {e_gemini}. Trying DeepSeek...")
            try:
                gaps, lessons = self._analyze_with_deepseek(historical, recommended)
            except Exception as e_deepseek:
                # print(f"DeepSeek analysis failed: {e_deepseek}. Falling back to heuristics.")
                gaps, lessons = self._analyze_heuristically(historical, recommended)
        
        # 3. Calculate score
        score = self._calculate_adherence_score(gaps)
        
        return AnalysisReport(
            situation=historical,
            actual_decision=historical.actual_decision,
            actual_outcome=historical.actual_outcome,
            recommended_decision=recommended,
            gaps=gaps,
            lessons=lessons,
            principle_adherence_score=score
        )
    
    def what_would_principles_say(
        self, situation: HistoricalSituation
    ) -> DecisionResult:
        """Get what principles would recommend for a situation."""
        return self.engine.evaluate(situation)

    def _calculate_adherence_score(self, gaps: List[Gap]) -> float:
        """Calculate adherence score based on gaps."""
        if not gaps:
            return 1.0
        
        total_severity = sum(g.severity for g in gaps)
        # Simple decay formula
        # 10 severity points => 0.5 score roughly
        score = max(0.0, 1.0 - (total_severity * 0.05))
        return round(score, 2)

    def _analyze_with_gemini(
        self, historical: HistoricalSituation, recommended: DecisionResult
    ) -> tuple[List[Gap], List[Lesson]]:
        """Analyze using Gemini API."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Gemini API key not configured")
        
        model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        endpoint = os.getenv(
            "GEMINI_API_ENDPOINT",
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        )
        
        # If endpoint uses a different model than configured, update it
        if ":generateContent" in endpoint and model not in endpoint:
             base = endpoint.split("/models/")[0]
             endpoint = f"{base}/models/{model}:generateContent"
            
        # print(f"DEBUG: Querying Gemini at {endpoint} with {model}...")

        prompt = self._construct_prompt(historical, recommended)
        
        # Gemini specific payload
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        response = requests.post(
            f"{endpoint}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=payload
        )
        response.raise_for_status()

        data = response.json()
        
        # Extract text from Gemini response structure
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
            return self._parse_llm_json(text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse Gemini response: {e}")

    def _analyze_with_deepseek(
        self, historical: HistoricalSituation, recommended: DecisionResult
    ) -> tuple[List[Gap], List[Lesson]]:
        """Analyze using DeepSeek API (OpenAI compatible)."""
        api_key = os.getenv("DEEPSEEK_API_KEY")
        endpoint = os.getenv("DEEPSEEK_API_ENDPOINT")
        model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        if not api_key or "PLACEHOLDER" in api_key:
            raise ValueError("DeepSeek API key not configured")
            
        prompt = self._construct_prompt(historical, recommended)
        
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a decision analysis assistant. Return ONLY JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(
            endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        
        try:
            text = data["choices"][0]["message"]["content"]
            return self._parse_llm_json(text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ValueError(f"Failed to parse DeepSeek response: {e}")

    def _construct_prompt(
        self, historical: HistoricalSituation, recommended: DecisionResult
    ) -> str:
        """Construct the analysis prompt."""
        return f"""
        Analyze the following decision situation against the recommended principles.
        
        SITUATION:
        {historical.description}
        
        ACTUAL DECISION:
        {historical.actual_decision}
        
        ACTUAL OUTCOME:
        {historical.actual_outcome}
        
        RECOMMENDED PRINCIPLES (& ACTION):
        {recommended.recommendation}
        {recommended.reasoning}
        
        TASK:
        Identify gaps between the ACTUAL decision and the RECOMMENDED course.
        Extract lessons for the future.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "gaps": [
                {{ "gap_type": "string", "description": "string", "severity": 1-10 }}
            ],
            "lessons": [
                {{ "insight": "string", "actionable": "string" }}
            ]
        }}
        """

    def _parse_llm_json(self, text: str) -> tuple[List[Gap], List[Lesson]]:
        """Parse JSON response from LLM."""
        # potential cleanup of markdown code blocks
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        data = json.loads(clean_text)
        
        gaps = [Gap(**g) for g in data.get("gaps", [])]
        lessons = [Lesson(**l) for l in data.get("lessons", [])]
        return gaps, lessons

    def _analyze_heuristically(
        self, historical: HistoricalSituation, recommended: DecisionResult
    ) -> tuple[List[Gap], List[Lesson]]:
        """Fallback keyword-based analysis."""
        gaps = []
        lessons = []
        
        actual_text = historical.actual_decision.lower()
        rec_text = recommended.recommendation.lower()
        
        # 1. Check for missing principle keywords
        for match in recommended.applicable_principles:
            p = match.principle
            # Check if title or key tags are missing
            if p.title.lower() not in actual_text:
                # Check tags
                missing_tags = [t for t in p.tags if t.lower() not in actual_text]
                if len(missing_tags) > len(p.tags) / 2:
                    gaps.append(Gap(
                        gap_type="missed_principle",
                        description=f"Decision missed applying principle: {p.title}",
                        severity=7
                    ))
                    lessons.append(Lesson(
                        principle_id=p.id,
                        insight=f"Need to better incorporate '{p.title}' in similar situations.",
                        actionable=f"Review principle {p.id} checklist before deciding."
                    ))

        # 2. Check for negative outcome correlations
        negative_outcomes = ["regret", "fail", "bad", "loss", "error", "poor", "worse"]
        if any(w in historical.actual_outcome.lower() for w in negative_outcomes):
            if not gaps:
                gaps.append(Gap(
                    gap_type="bad_outcome_blindspot",
                    description="Outcome was poor but specific principle violation not detected by keywords.",
                    severity=5
                ))
                lessons.append(Lesson(
                    insight="Outcome suggests a gap in execution or undefined principle.",
                    actionable="Reflect on this decision to identify new principles."
                ))
        
        if not gaps:
             # If no specific gaps found but texts are very different
             pass 

        return gaps, lessons
