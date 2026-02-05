# ⚡ NVIDIA Nano Agent

> **Local Inference Agent for Edge Computing and Offline AI**

## 📋 Overview

The **NVIDIA Nano Agent** is designed for running AI inference locally, particularly on edge devices like NVIDIA Jetson Nano. It provides:

- 🔍 **Code Analysis** - Find bugs, issues, and improvements
- ✅ **Project Validation** - Check structure completeness
- 📚 **Quick Documentation** - Auto-generate docstrings
- 📦 **Dependency Analysis** - Check for issues in requirements

---

## ⚡ Quick Start

### Prerequisites

```bash
# Basic requirements
pip install openai requests

# Optional: Install Ollama for local inference
# Download from: https://ollama.ai
```

### Running the Agent

```bash
cd "c:\Users\Admin\Desktop\KARYA AGENT"
python NvidiaNanoAgent.py
```

---

## 🔧 Configuration

### Local Inference (Ollama)

```bash
# Install Ollama and pull a model
ollama pull codellama:7b

# Start Ollama server
ollama serve
```

The agent will automatically detect and use Ollama if available.

### Cloud Fallback

Set your API key for cloud inference:

```bash
set OPENROUTER_API_KEY=your-api-key
```

---

## 🎯 Features

### 1. Code Analysis

```python
from NvidiaNanoAgent import NvidiaNanoAgent

agent = NvidiaNanoAgent()
result = agent.analyze_code('''
def calculate(x, y):
    return x / y  # Potential division by zero!
''')
print(result["analysis"])
```

### 2. Project Validation

```python
structure = {
    "src": ["main.py", "utils.py"],
    "tests": [],
    "docs": []
}
result = agent.validate_project_structure(structure)
print(result["validation"])
```

### 3. Quick Documentation

```python
code = '''
def process_data(items, filter_fn):
    return [x for x in items if filter_fn(x)]
'''
docs = agent.generate_quick_docs(code)
print(docs)
```

### 4. Dependency Check

```python
deps = ["flask==2.0.0", "numpy", "pandas>=1.0"]
result = agent.check_dependencies(deps)
print(result["analysis"])
```

---

## 🌐 Inference Modes

| Mode | Requirements | Speed | Privacy |
|------|--------------|-------|---------|
| **Local (Ollama)** | Ollama installed | Fast | 100% Private |
| **Cloud (OpenRouter)** | API Key | Medium | Sent to cloud |

The agent automatically selects local mode if available.

---

## 📊 Supported Languages

- Python
- JavaScript/TypeScript
- Java
- Go
- Rust
- C/C++
- C#
- Ruby
- PHP

---

## 🔌 Integration with Other Agents

```python
from NvidiaNanoAgent import NvidiaNanoAgent
from ProjectDevAgent import ProjectArchitect

# Generate project structure
architect = ProjectArchitect()
result = architect.analyze_project("A Flask REST API")

# Validate the structure locally
nano = NvidiaNanoAgent(use_local=True)
validation = nano.validate_project_structure(result["structure"])
```

---

## 🐛 Troubleshooting

**Ollama not detected:**
```bash
# Ensure Ollama is running
curl http://localhost:11434/api/tags
```

**Slow inference:**
```bash
# Use a smaller model
ollama pull tinyllama
# Edit DEFAULT_MODEL in NvidiaNanoAgent.py
```

---

*Built with ❤️ by KARYA AGENT System*
