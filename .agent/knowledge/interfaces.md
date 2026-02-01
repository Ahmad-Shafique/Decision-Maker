# Interfaces Documentation

## Overview
The system exposes its core logic through two primary interfaces:
1. **CLI (Command Line Interface)**: For direct, interactive, or scripted usage.
2. **REST API**: For integration with web frontends or external systems.

## CLI (`src/interfaces/cli.py`)
Built using `typer` and `rich`.

### Commands
- `analyze`: Evaluates a new situation.
  - `--situation "text"`: Direct input.
  - `--file path/to/sit.yaml`: Load from file.
  - `--output path/to/report.md`: Save report.
- `history`: Analyzes a past decision using the Historical Analyzer.
  - `--file`: Path to historical situation YAML.

## REST API (`src/interfaces/api.py`)
Built using `FastAPI` and `uvicorn`.

### Configuration
- **Port**: 2947 (Custom)
- **Host**: 127.0.0.1 (Localhost)

### Endpoints
- `GET /health`: System status check.
- `GET /principles`: List all loaded principles.
- `POST /analyze`: Core decision endpoint.
  - **Payload**: `{"description": "Situation text..."}`
  - **Response**: Full `DecisionResult` JSON object.

### Architecture provided
- **Lifespan Context**: Initializes `KnowledgeBase` and `DecisionEngine` (with Semantic Matching) on startup to ensure high performance (loading happens once).
