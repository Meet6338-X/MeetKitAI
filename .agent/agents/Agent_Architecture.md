# 🧠 Agent Architecture Documentation

> **Technical deep-dive into the Project Development Agent's internal architecture**

---

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INPUT                                       │
│                    (Project Description)                                 │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PROJECT ARCHITECT                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    LLM API CLIENT                                │   │
│  │              (OpenRouter → Multiple Models)                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                   │                                      │
│           ┌───────────────────────┼───────────────────────┐             │
│           ▼                       ▼                       ▼             │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐       │
│  │  STRUCTURE      │   │  EXECUTION      │   │  README         │       │
│  │  GENERATOR      │   │  PLANNER        │   │  GENERATOR      │       │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT FILES                                     │
│    • PROJECT_OVERVIEW.md  • PROJECT_STRUCTURE.md  • EXECUTION_PLAN.md   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎭 Persona System Prompt

The agent uses a carefully crafted **System Prompt** to establish its persona:

```python
ARCHITECT_SYSTEM_PROMPT = """
You are a Senior Technical Architect with 15+ years of experience 
in building production-level systems.

Your expertise includes:
- System Design & Architecture
- Microservices, Monoliths, and Serverless patterns
- Frontend (React, Vue, Angular, Next.js)
- Backend (Python/FastAPI, Node.js, Go, Java/Spring)
- Databases (PostgreSQL, MongoDB, Redis, Elasticsearch)
- DevOps (Docker, Kubernetes, CI/CD, Terraform)
- Cloud Platforms (AWS, GCP, Azure)

When given a project idea, you will provide:
1. A comprehensive analysis of requirements
2. Technology stack recommendations with justifications
3. A detailed project structure
4. A phased execution plan

Always think about:
- Scalability & Performance
- Security best practices
- Maintainability & Code quality
- Testing strategies
- Documentation needs
- Error handling & Logging
"""
```

### Why This Persona Works

| Aspect | Implementation |
|--------|----------------|
| **Authority** | "Senior" + "15+ years" establishes credibility |
| **Breadth** | Lists multiple technology domains |
| **Output Format** | Explicitly states deliverables |
| **Quality Anchor** | Production-level focus |

---

## 🔄 Processing Pipeline

### Stage 1: Input Normalization

```python
def _generate_project_name(self, description: str) -> str:
    """Generate a suitable project name from description."""
    words = description.split()[:5]
    name = "_".join(words).lower()
    name = "".join(c if c.isalnum() or c == "_" else "" for c in name)
    return name[:30] or "new_project"
```

### Stage 2: Structure Generation

**Prompt Template:**
```python
STRUCTURE_PROMPT_TEMPLATE = """
Based on the following project description, generate a 
comprehensive directory structure for a production-level project.

PROJECT DESCRIPTION:
{project_description}

Provide the output in the following format:
## Recommended Technology Stack
## Project Directory Structure
## Key Files Description
## Configuration Files Needed
"""
```

**Example Output:**
```
project-name/
├── src/
│   ├── api/
│   │   ├── routes/
│   │   └── middleware/
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── models/
│   ├── services/
│   └── utils/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── docker/
├── .github/
│   └── workflows/
└── scripts/
```

### Stage 3: Execution Plan Generation

**Prompt Template:**
```python
EXECUTION_PLAN_PROMPT_TEMPLATE = """
Based on the following project description and structure, 
create a detailed step-by-step execution plan.

PROJECT DESCRIPTION:
{project_description}

PROJECT STRUCTURE:
{project_structure}

Provide a phased execution plan...
"""
```

**Key Feature:** The execution plan receives the **already generated structure** as context, enabling coherent, aligned recommendations.

---

## 🔧 LLM Interaction

### API Call Structure

```python
def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
    response = self.client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,  # Balance creativity and consistency
        max_tokens=4000   # Allow comprehensive responses
    )
    return response.choices[0].message.content
```

### Temperature Selection Rationale

| Temperature | Use Case |
|-------------|----------|
| 0.0 - 0.3 | Strict, deterministic (code generation) |
| **0.5 - 0.7** | **Balanced (our choice)** |
| 0.8 - 1.0 | Creative, diverse (brainstorming) |

We use **0.7** to get creative but consistent architectural recommendations.

---

## 📁 Output File Generation

```python
def _save_outputs(self) -> dict:
    # Create timestamped directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    project_dir = os.path.join(
        OUTPUT_DIR, 
        f"{self.project_name}_{timestamp}"
    )
    
    # Generate four files:
    # 1. PROJECT_OVERVIEW.md   - Original input + metadata
    # 2. PROJECT_STRUCTURE.md  - Directory tree + tech stack
    # 3. EXECUTION_PLAN.md     - Phased implementation
    # 4. README.md             - Combined, user-friendly doc
```

---

## 🛡️ Error Handling

```python
def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
    try:
        response = self.client.chat.completions.create(...)
        return response.choices[0].message.content
    except Exception as e:
        return f"Error calling LLM: {str(e)}"
```

### Future Improvements
- [ ] Retry logic with exponential backoff
- [ ] Fallback to alternative models
- [ ] Partial result caching
- [ ] Input validation

---

## 🔌 Extension Points

### Adding New Output Types

```python
# In _save_outputs(), add new file generation:
api_doc_path = os.path.join(project_dir, "API_SPECIFICATION.md")
with open(api_doc_path, "w") as f:
    f.write(self._generate_api_spec())
```

### Custom System Prompts

```python
# Create domain-specific architects:
MOBILE_ARCHITECT_PROMPT = """
You are a Mobile App Architect specializing in...
"""

# Use different prompts for different project types
if "mobile" in description.lower():
    system_prompt = MOBILE_ARCHITECT_PROMPT
```

### Multi-Agent Orchestration

```python
# Future: Chain multiple specialized agents
from NvidiaNanoAgent import LocalInference
from UltraContextAgent import ContextExpander

# 1. Expand context with UltraContextAgent
expanded = ContextExpander().process(description)

# 2. Generate architecture with ProjectArchitect
architecture = ProjectArchitect().analyze_project(expanded)

# 3. Validate locally with NvidiaNanoAgent
validated = LocalInference().validate(architecture)
```

---

## 📈 Performance Characteristics

| Metric | Typical Value |
|--------|---------------|
| Structure Generation | 5-10 seconds |
| Execution Plan | 8-15 seconds |
| Total Processing | 15-30 seconds |
| Output Size | 10-50 KB |

---

## 🔮 Future Roadmap

1. **Interactive Mode** - Ask clarifying questions
2. **Code Scaffolding** - Generate actual boilerplate code
3. **Version Control Integration** - Auto-commit to Git
4. **Template Library** - Quick-start from common patterns
5. **Cost Estimation** - Infrastructure pricing analysis

---

*Documentation Version: 1.0.0*
*Last Updated: February 2026*
