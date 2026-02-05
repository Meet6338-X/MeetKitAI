# 🧠 Ultra Context Agent

> **Extended Context Processing for Large Codebases**

## 📋 Overview

The **Ultra Context Agent** handles scenarios requiring massive context windows. It can analyze entire codebases by:

- 📂 **Scanning directories** - Automatically find relevant files
- 📦 **Chunking content** - Split large codebases into manageable pieces
- 🔍 **Analyzing chunks** - Process each chunk with AI
- 📝 **Synthesizing reports** - Combine analyses into comprehensive docs

---

## ⚡ Quick Start

### Prerequisites

```bash
pip install openai
```

### Running the Agent

```bash
cd "c:\Users\Admin\Desktop\KARYA AGENT"
python UltraContextAgent.py
```

---

## 🎯 Features

### 1. Codebase Analysis

Analyze an entire project directory:

```python
from UltraContextAgent import UltraContextAgent

agent = UltraContextAgent()
result = agent.analyze_codebase("C:/path/to/project")

print(result["final_report"])
```

**Output includes:**
- Executive Summary
- Architecture Overview
- Key Components
- Technology Stack
- Code Quality Assessment
- Recommendations

### 2. Documentation Generation

Auto-generate documentation:

```python
# Generate README
readme = agent.generate_documentation("./project", doc_type="readme")

# Generate API docs
api_docs = agent.generate_documentation("./project", doc_type="api")

# Generate architecture docs
arch_docs = agent.generate_documentation("./project", doc_type="architecture")
```

### 3. Ask Questions

Query the codebase:

```python
answer = agent.answer_question(
    "./project",
    "How does the authentication system work?"
)
print(answer)
```

---

## 📊 Context Management

### How Chunking Works

```
Large Codebase (500 files, 2M tokens)
           │
           ▼
    ┌──────────────┐
    │ File Scanner │  ← Filters by extension, ignores node_modules etc.
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │   Chunker    │  ← Splits into ~50K token chunks
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │ Per-Chunk    │  ← Analyzes each chunk individually
    │  Analysis    │
    └──────────────┘
           │
           ▼
    ┌──────────────┐
    │ Synthesizer  │  ← Combines into final report
    └──────────────┘
```

### File Type Support

| Category | Extensions |
|----------|------------|
| **Code** | .py, .js, .ts, .java, .go, .rs, .cpp, .c, .cs, .rb, .php |
| **Docs** | .md, .txt, .rst, .adoc |
| **Config** | .json, .yaml, .yml, .toml, .ini, .env |

### Ignored Directories

By default, these are skipped:
- `node_modules`
- `__pycache__`
- `.git`
- `.venv` / `venv`
- `dist` / `build`
- `.next`
- `coverage`

---

## ⚙️ Configuration

### Model Tiers

```python
# Use the ultra tier (1M context)
agent = UltraContextAgent(model_tier="ultra")

# Use large tier (200K context)
agent = UltraContextAgent(model_tier="large")

# Use standard tier (128K context)
agent = UltraContextAgent(model_tier="standard")
```

| Tier | Model | Context Window |
|------|-------|----------------|
| ultra | gemini-2.0-flash | 1M tokens |
| large | claude-3.5-sonnet | 200K tokens |
| standard | gpt-4o | 128K tokens |

### Custom API Key

```python
agent = UltraContextAgent(
    api_key="your-openrouter-key",
    model_tier="ultra"
)
```

---

## 🔧 Programmatic Usage

### Context Builder Standalone

```python
from UltraContextAgent import ContextBuilder

# Build context manually
builder = ContextBuilder(max_tokens=100000)
builder.add_directory("./src")
builder.add_file("./README.md")

# Get summary
print(builder.get_context_summary())

# Build chunks
chunks = builder.build_chunks()
for chunk in chunks:
    print(f"{chunk.chunk_id}: {len(chunk.source_files)} files")
```

### Custom Analysis Pipeline

```python
agent = UltraContextAgent()

# Step 1: Add files
agent.context_builder.add_directory("./backend")
agent.context_builder.add_directory("./frontend")

# Step 2: Build chunks
chunks = agent.context_builder.build_chunks()

# Step 3: Custom processing
for chunk in chunks:
    # Your custom analysis logic
    pass
```

---

## 🔌 Integration with Other Agents

```python
from UltraContextAgent import UltraContextAgent
from ProjectDevAgent import ProjectArchitect

# Analyze existing project
ultra = UltraContextAgent()
analysis = ultra.analyze_codebase("./existing-project")

# Generate improvement plan
architect = ProjectArchitect()
plan = architect.analyze_project(f"""
Improve this existing project based on analysis:
{analysis['final_report']}
""")
```

---

## 📈 Performance Tips

1. **Limit directory depth** for faster scanning
2. **Use specific extensions** to reduce file count
3. **Start with smaller model tiers** for cost efficiency
4. **Cache analysis results** for repeated queries

---

## 🐛 Troubleshooting

**Out of memory:**
```python
# Reduce chunk size
builder = ContextBuilder(max_tokens=25000)
```

**API timeout:**
```python
# Use a faster model
agent = UltraContextAgent(model_tier="standard")
```

**Missing files:**
```python
# Add custom extensions
builder.add_directory("./src", extensions=[".py", ".pyi"])
```

---

*Built with ❤️ by KARYA AGENT System*
