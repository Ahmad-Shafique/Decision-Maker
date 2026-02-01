"""Report Generator - Creates human-readable reports from analysis results.

This module is responsible for formatting decision results and historical
analyses into clean, readable Markdown reports.
"""

from typing import Optional
from datetime import datetime

from src.engine.models import DecisionResult, PrincipleMatch
from src.analyzer.historical_analyzer import AnalysisReport, Gap, Lesson
from src.domain.principles import Principle
from src.domain.sops import SOP
from src.domain.situations import Situation, HistoricalSituation


class ReportGenerator:
    """Generates Markdown reports for various system outputs."""
    
    def generate_decision_report(self, result: DecisionResult) -> str:
        """Generate a report for a decision recommendation.
        
        Args:
            result: The decision result to report on.
            
        Returns:
            Markdown string containing the report.
        """
        situation = result.situation
        
        sections = [
            f"# Decision Analysis Report",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            f"**Situation Override:** {situation.description[:100]}...",
            "",
            "## 1. Situation Context",
            f"- **Description:** {situation.description}",
            f"- **Domain:** {situation.domain}",
            f"- **Stakes:** {situation.stakes}",
            f"- **Emotions:** {', '.join(situation.context.emotions) if situation.context.emotions else 'None recorded'}",
            "",
            "## 2. Applicable Principles",
        ]
        
        if result.applicable_principles:
            for match in result.applicable_principles:
                p = match.principle
                sections.append(f"### {p.id}. {p.title}")
                sections.append(f"**Relevance:** {match.relevance_score:.2f} | **Reason:** {match.match_reason}")
                sections.append(f"_{p.sub_principles[0].text if p.sub_principles else 'No specific sub-principles'}_")
                sections.append("")
        else:
            sections.append("_No specific principles found matching this situation._")
            sections.append("")
            
        sections.append("## 3. Triggered SOPs")
        if result.triggered_sops:
            for sop in result.triggered_sops:
                sections.append(f"- **{sop.name}**: {sop.purpose}")
        else:
            sections.append("_No Standard Operating Procedures triggered._")
            
        sections.append("")
        sections.append("## 4. Recommendation")
        sections.append(result.recommendation)
        sections.append("")
        sections.append(f"**Reasoning:** {result.reasoning}")
        sections.append(f"**Confidence:** {result.confidence:.2f}")
        
        return "\n".join(sections)
    
    def generate_historical_report(self, report: AnalysisReport) -> str:
        """Generate a report for a historical analysis.
        
        Args:
            report: The analysis report to format.
            
        Returns:
            Markdown string containing the report.
        """
        hist = report.situation
        rec = report.recommended_decision
        
        sections = [
            f"# Historical Analysis: {hist.description[:50]}...",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "## 1. accurate Record",
            f"**What Happened:** {hist.description}",
            f"**Actual Decision:** {report.actual_decision}",
            f"**Outcome:** {report.actual_outcome}",
            "",
            "## 2. Principle-Based Analysis",
            f"**Adherence Score:** {report.principle_adherence_score:.2f}/1.0",
            "",
            "### Recommended Course",
            rec.recommendation,
            "",
            "### Analysis of Gaps",
        ]
        
        if report.gaps:
            for gap in report.gaps:
                sections.append(f"- **[{gap.gap_type.upper()}]** {gap.description} (Severity: {gap.severity})")
        else:
            sections.append("_No significant gaps identified._")
            
        sections.append("")
        sections.append("## 3. Lessons Learned")
        if report.lessons:
            for lesson in report.lessons:
                sections.append(f"- **Insight:** {lesson.insight}")
                sections.append(f"  **Action:** {lesson.actionable}")
        else:
            sections.append("_No specific lessons extracted._")
            
        return "\n".join(sections)
