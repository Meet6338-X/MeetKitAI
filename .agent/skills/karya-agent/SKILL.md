---
name: karya-agent
description: KARYA AGENT v3.5 - Multi-agent AI framework for autonomous project development. 12 specialized agents, project profiles, validation pipeline, plugin system.
---

# KARYA AGENT v3.5

> Multi-Agent AI Framework for Autonomous Production-Level Project Development

## Overview

KARYA AGENT is a sophisticated multi-agent system that autonomously analyzes requirements, designs architecture, and generates complete, production-ready codebases using Google Gemini.

## Key Features

- **🧠 12 Specialized Agents**: ProjectLeadAI, TechArchitectAI, DataEngineerAI, FrontendAI, BackendAI, FeatureAI, DevOpsAI, SecurityAI, IntegrationAI, PresentationAI, EvaluationAI, FeedbackLoopAI
- **🎭 Project Profiles**: web_app, ml_project, mobile_app, cli_tool, microservices, api_backend, data_pipeline, iot_project
- **🛡️ Validation Pipeline**: Pre/post checks, quality gates, security scanning
- **🔌 Plugin System**: Extensible architecture for custom agents
- **📚 Template Library**: Pre-built project starters

## Available Agents

| Agent | File | Purpose |
|-------|------|---------|
| AI Project Brigade | `AIProjectBrigade.py` | Multi-agent orchestrator (12 agents) |
| Project Dev Agent | `ProjectDevAgent.py` | Single-agent project scaffolding |
| NVIDIA Nano Agent | `NvidiaNanoAgent.py` | Edge/local inference agent |
| Ultra Context Agent | `UltraContextAgent.py` | Large codebase analysis |
| GLM Agent | `GLMAgent.py` | Reasoning agent |

## Quick Start

```bash
# Set API key
set OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Run the multi-agent system
python .agent/skills/karya-agent/AIProjectBrigade.py "Your project description"

# Or run single-agent mode
python .agent/skills/karya-agent/ProjectDevAgent.py
```

## Project Profiles

Configure via `--profile <name>` or let auto-detection choose:

| Profile | Tech Stack |
|---------|------------|
| `web_app` | React + FastAPI + PostgreSQL |
| `ml_project` | PyTorch + FastAPI + MLflow |
| `mobile_app` | React Native + Firebase |
| `cli_tool` | Python + Click/Typer |
| `microservices` | Docker + Kubernetes |

## Configuration

Edit `config.yaml` to customize:
- API settings and model assignments
- Agent enable/disable toggles
- Validation thresholds
- Plugin configuration
- Interactive mode checkpoints

## Templates

Available in `.agent/templates/`:
- `fullstack-react-fastapi/` - Full-stack starter
- `cli-tool/` - CLI application
- `ml-pipeline/` - ML training pipeline
- `microservices/` - Distributed systems
- `project-scaffold/` - Hackathon-ready scaffold

## Documentation

- `README.md` - Main documentation
- `AIProjectBrigade_README.md` - Brigade system docs
- `ProjectDevAgent_README.md` - Dev agent docs
- `Agent_Architecture.md` - Technical architecture
- `v4_roadmap.md` - Future plans

## Cross-References

- `@[skills/app-builder]` - Application building patterns
- `@[skills/architecture]` - Architectural decisions
- `@[skills/deployment-procedures]` - Deployment workflows
