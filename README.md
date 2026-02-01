# Principles-Based Decision System

A modular, object-oriented system that encodes personal values and principles to assist in decision-making and analyze historical situations.

## Overview

This system transforms your personal values, principles, and Standard Operating Procedures (SOPs) into an actionable decision-support tool. It can:

- **Analyze situations** against your principles framework
- **Recommend decisions** aligned with your values
- **Review historical situations** to understand what principles would have suggested
- **Track patterns** in decision-making over time

## Project Structure

```
src/
├── domain/      # Core domain models (Values, Principles, SOPs, Situations)
├── knowledge/   # Knowledge base for storing and querying principles
├── engine/      # Decision engine that applies principles to situations
├── analyzer/    # Historical analysis module
├── reporting/   # Report generation
└── interfaces/  # CLI and API interfaces

data/            # Your encoded values, principles, and SOPs in YAML
tests/           # Test suite
.agent/          # AI agent context files for development assistance
```

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the CLI
python -m src.interfaces.cli --help

# Analyze a situation
python -m src.interfaces.cli analyze --situation "Description of your situation"
```

## Development

See `.agent/context/development.md` for coding standards and patterns.

## License

Private - Personal Use Only
