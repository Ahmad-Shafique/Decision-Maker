"""CLI Interface - Command line entry point.

This module provides the command-line interface for interacting with the
decision system. It allows users to analyze new situations and review
historical decisions.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich.console import Console
from rich.markdown import Markdown

from src.domain.situations import Situation, HistoricalSituation
from src.knowledge.knowledge_base import KnowledgeBase
from src.engine.decision_engine import DecisionEngine
from src.analyzer.historical_analyzer import HistoricalAnalyzer
from src.reporting.generator import ReportGenerator


app = typer.Typer(
    name="principles-cli",
    help="Principles-Based Decision System CLI",
    add_completion=False,
)
console = Console()


def get_components():
    """Initialize system components.
    
    Returns:
        Tuple of (KnowledgeBase, DecisionEngine, HistoricalAnalyzer, ReportGenerator)
    """
    # Assuming the CLI is run from the project root
    data_path = Path("data")
    if not data_path.exists():
        # Fallback to looking relative to the module if installed
        data_path = Path(__file__).parent.parent.parent / "data"
    
    if not data_path.exists():
        console.print("[bold red]Error:[/bold red] Could not find data directory.")
        sys.exit(1)
        
    kb = KnowledgeBase(data_path=data_path)
    kb.load()
    
    engine = DecisionEngine(knowledge_base=kb)
    analyzer = HistoricalAnalyzer(decision_engine=engine)
    reporter = ReportGenerator()
    
    return kb, engine, analyzer, reporter


@app.command()
def analyze(
    situation: str = typer.Option(None, "--situation", "-s", help="Description of the situation"),
    file: Path = typer.Option(None, "--file", "-f", help="Path to YAML file containing situation"),
    output: Path = typer.Option(None, "--output", "-o", help="Save report to file")
):
    """Analyze a situation and get recommendations."""
    kb, engine, _, reporter = get_components()
    
    target_situation = None
    
    if file:
        if not file.exists():
            console.print(f"[bold red]Error:[/bold red] File not found: {file}")
            raise typer.Exit(code=1)
        
        with open(file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            # Handle both raw dict and list wrapped dicts
            if isinstance(data, list):
                data = data[0]
            target_situation = Situation(**data)
            
    elif situation:
        # Create a simple situation from the description
        import uuid
        target_situation = Situation(
            id=str(uuid.uuid4()),
            description=situation
        )
    else:
        console.print("[bold red]Error:[/bold red] Must provide either --situation or --file")
        raise typer.Exit(code=1)
    
    with console.status("[bold green]Analyzing situation...[/bold green]"):
        result = engine.evaluate(target_situation)
        report = reporter.generate_decision_report(result)
    
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(report)
        console.print(f"[bold green]Report saved to {output}[/bold green]")
    else:
        console.print(Markdown(report))


@app.command()
def history(
    file: Path = typer.Option(..., "--file", "-f", help="Path to YAML file containing historical situation"),
    output: Path = typer.Option(None, "--output", "-o", help="Save report to file")
):
    """Analyze a past decision against principles."""
    _, _, analyzer, reporter = get_components()
    
    if not file.exists():
        console.print(f"[bold red]Error:[/bold red] File not found: {file}")
        raise typer.Exit(code=1)
        
    with open(file, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        if isinstance(data, list):
            data = data[0]
        target_situation = HistoricalSituation(**data)
    
    with console.status("[bold green]Analyzing history...[/bold green]"):
        path_report = analyzer.analyze(target_situation)
        report_text = reporter.generate_historical_report(path_report)

    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(report_text)
        console.print(f"[bold green]Report saved to {output}[/bold green]")
    else:
        console.print(Markdown(report_text))


if __name__ == "__main__":
    app()
