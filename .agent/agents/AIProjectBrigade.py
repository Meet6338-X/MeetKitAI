"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                           🏭 AI PROJECT BRIGADE - ORCHESTRATOR v3.0                              ║
║                    Multi-Agent System for Autonomous Project Development                          ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

A complete AI-powered project factory that orchestrates multiple specialized agents to:
- Analyze requirements and create project plans
- Generate complete code, documentation, and assets
- Build, test, and deploy production-ready projects
- Create presentations, demos, and evaluation metrics

Agent Team:
├── ProjectLeadAI      - Coordinator, task assignment, milestone tracking
├── TechArchitectAI    - System design, architecture diagrams, module specs
├── DataEngineerAI     - Data collection, cleaning, API integration
├── FrontendAI         - UI/UX, dashboards, responsive components
├── BackendAI          - APIs, business logic, database integration
├── FeatureAI          - AI/ML models, core automation, predictions
├── PresentationAI     - PPT slides, visualizations, mockups
├── IntegrationAI      - Testing, QA, module integration
├── EvaluationAI       - KPIs, scoring predictions, metrics
├── DevOpsAI           - Deployment, CI/CD, monitoring
├── SecurityAI         - Risk assessment, compliance, security
└── FeedbackLoopAI     - Continuous improvement, model refinement

Author: KARYA AGENT System
Version: 3.0.0
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from openai import OpenAI
import threading
import queue
import time

# Fix unicode output in Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECTS_DIR = os.path.join(BASE_DIR, "projects")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
BASE_URL = "https://openrouter.ai/api/v1"

# Model configurations for different agent types
MODELS = {
    "reasoning": "google/gemini-2.0-flash-001",      # For planning, architecture
    "coding": "google/gemini-2.0-flash-001",          # For code generation
    "creative": "google/gemini-2.0-flash-001",        # For presentations, docs
    "analysis": "google/gemini-2.0-flash-001",        # For evaluation, metrics
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s',
    datefmt='%H:%M:%S'
)


# ══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES & ENUMS
# ══════════════════════════════════════════════════════════════════════════════

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


class TaskPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class AgentTask:
    """A task assigned to an agent."""
    task_id: str
    agent_name: str
    description: str
    inputs: Dict[str, Any]
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    output: Any = None
    error: str = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = None


@dataclass
class ProjectContext:
    """Shared context for all agents."""
    project_name: str
    project_dir: str
    description: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    files_created: List[str] = field(default_factory=list)
    tasks: List[AgentTask] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    status: str = "initializing"


# ══════════════════════════════════════════════════════════════════════════════
# BASE AGENT CLASS
# ══════════════════════════════════════════════════════════════════════════════

class BaseAgent:
    """Base class for all AI agents."""
    
    def __init__(self, name: str, role: str, model_type: str = "reasoning"):
        self.name = name
        self.role = role
        self.model = MODELS.get(model_type, MODELS["reasoning"])
        self.status = AgentStatus.IDLE
        self.logger = logging.getLogger(name)
        self.client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the agent's system prompt."""
        return f"""You are {self.name}, a specialized AI agent in the Project Brigade.
Your role: {self.role}

You are part of a multi-agent system building production-level projects.
Always provide complete, working outputs - never placeholders.
Format outputs clearly and follow best practices.
"""
    
    def _call_llm(self, prompt: str, max_tokens: int = 4000) -> str:
        """Make an LLM API call."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"LLM Error: {e}")
            return f"Error: {str(e)}"
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        """Process a task. Override in subclasses."""
        raise NotImplementedError


# ══════════════════════════════════════════════════════════════════════════════
# SPECIALIZED AGENTS
# ══════════════════════════════════════════════════════════════════════════════

class ProjectLeadAI(BaseAgent):
    """Project coordinator and task manager."""
    
    def __init__(self):
        super().__init__(
            name="ProjectLeadAI",
            role="Project Lead / Product Manager - Coordinates all agents, defines milestones, assigns tasks"
        )
        self.system_prompt += """
You analyze project requirements and create:
1. Clear project goals and scope
2. Task breakdown for each agent
3. Priority assignments and dependencies
4. Milestone tracking

Output format: JSON with tasks, milestones, and agent assignments.
"""
    
    def analyze_requirements(self, description: str) -> Dict:
        """Analyze project and create task plan."""
        prompt = f"""Analyze this project and create a comprehensive task plan:

PROJECT DESCRIPTION:
{description}

Create a JSON response with:
{{
    "project_name": "kebab-case-name",
    "summary": "One paragraph summary",
    "goals": ["Goal 1", "Goal 2"],
    "scope": {{
        "in_scope": ["Feature 1"],
        "out_of_scope": ["Feature X"]
    }},
    "tech_stack": {{
        "frontend": "recommended",
        "backend": "recommended",
        "database": "recommended",
        "other": []
    }},
    "agent_tasks": [
        {{
            "agent": "TechArchitectAI",
            "task": "Design system architecture",
            "priority": "HIGH",
            "dependencies": []
        }}
    ],
    "milestones": [
        {{
            "name": "Foundation",
            "deliverables": ["Architecture", "Setup"],
            "timeline": "Day 1-2"
        }}
    ]
}}
"""
        response = self._call_llm(prompt)
        try:
            # Extract JSON from response
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"error": "Failed to parse requirements", "raw": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.analyze_requirements(context.description)


class TechArchitectAI(BaseAgent):
    """System architecture designer."""
    
    def __init__(self):
        super().__init__(
            name="TechArchitectAI",
            role="Technical Lead / System Architect - Designs architecture, module interfaces"
        )
        self.system_prompt += """
You design production-level architectures including:
1. System diagrams (describe in ASCII or Mermaid)
2. Module specifications
3. API contracts
4. Database schemas
5. Integration patterns

Focus on scalability, security, and maintainability.
"""
    
    def design_architecture(self, requirements: Dict) -> Dict:
        """Design system architecture."""
        prompt = f"""Design a complete system architecture for:

{json.dumps(requirements, indent=2)}

Provide:
1. High-level architecture diagram (Mermaid format)
2. Module specifications with interfaces
3. Database schema
4. API endpoints list
5. Data flow description

Output as JSON with 'diagram', 'modules', 'database', 'api_endpoints', 'data_flow' keys.
"""
        response = self._call_llm(prompt, max_tokens=6000)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"architecture_description": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.design_architecture(context.requirements)


class DataEngineerAI(BaseAgent):
    """Data preparation and pipeline agent."""
    
    def __init__(self):
        super().__init__(
            name="DataEngineerAI",
            role="Data Engineer - Data collection, cleaning, API integration, ETL pipelines"
        )
        self.system_prompt += """
You handle all data-related tasks:
1. Data schema design
2. Sample data generation
3. API integration code
4. ETL pipeline scripts
5. Data validation logic

Generate production-ready Python code.
"""
    
    def generate_data_layer(self, architecture: Dict) -> Dict:
        """Generate data layer code."""
        prompt = f"""Based on this architecture:

{json.dumps(architecture, indent=2)}

Generate:
1. Database models (SQLAlchemy or similar)
2. Sample data generation script
3. Data validation schemas (Pydantic)
4. Migration scripts

Output as JSON with 'models_code', 'sample_data_code', 'schemas_code', 'migrations_code' keys.
Each value should be complete, working Python code.
"""
        response = self._call_llm(prompt, max_tokens=8000)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"data_layer_code": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_data_layer(context.architecture)


class FrontendAI(BaseAgent):
    """Frontend developer agent."""
    
    def __init__(self):
        super().__init__(
            name="FrontendAI",
            role="Frontend Developer - UI/UX, dashboards, responsive components",
            model_type="coding"
        )
        self.system_prompt += """
You build modern, beautiful frontend interfaces:
1. React/Vue/Next.js components
2. Responsive layouts with Tailwind
3. State management
4. API integration
5. Forms and validation

Generate complete, production-ready code with proper styling.
"""
    
    def generate_frontend(self, requirements: Dict, architecture: Dict) -> Dict:
        """Generate frontend code."""
        prompt = f"""Create frontend code for:

Requirements: {json.dumps(requirements, indent=2)}
Architecture: {json.dumps(architecture, indent=2)}

Generate a complete React application with:
1. Main App component
2. Layout components (Header, Sidebar, Footer)
3. Feature components based on requirements
4. API service layer
5. Styling (Tailwind or CSS)

Output as JSON with file paths as keys and code as values:
{{
    "src/App.jsx": "// Complete code...",
    "src/components/Layout.jsx": "// Complete code...",
    "src/services/api.js": "// Complete code...",
    "src/styles/index.css": "/* Complete styles... */"
}}
"""
        response = self._call_llm(prompt, max_tokens=8000)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"frontend_code": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_frontend(context.requirements, context.architecture)


class BackendAI(BaseAgent):
    """Backend developer agent."""
    
    def __init__(self):
        super().__init__(
            name="BackendAI",
            role="Backend Developer - APIs, business logic, database integration",
            model_type="coding"
        )
        self.system_prompt += """
You build robust backend systems:
1. FastAPI/Flask/Express APIs
2. Business logic implementation
3. Database operations
4. Authentication/Authorization
5. Error handling and logging

Generate complete, production-ready code with proper structure.
"""
    
    def generate_backend(self, requirements: Dict, architecture: Dict) -> Dict:
        """Generate backend code."""
        prompt = f"""Create backend code for:

Requirements: {json.dumps(requirements, indent=2)}
Architecture: {json.dumps(architecture, indent=2)}

Generate a complete FastAPI application with:
1. Main application entry point
2. Route handlers for all endpoints
3. Service layer with business logic
4. Database operations
5. Authentication middleware
6. Configuration management
7. requirements.txt

Output as JSON with file paths as keys and code as values:
{{
    "backend/main.py": "# Complete code...",
    "backend/routes/api.py": "# Complete code...",
    "backend/services/business.py": "# Complete code...",
    "backend/config.py": "# Complete code...",
    "backend/requirements.txt": "# Dependencies..."
}}
"""
        response = self._call_llm(prompt, max_tokens=8000)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"backend_code": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_backend(context.requirements, context.architecture)


class FeatureAI(BaseAgent):
    """AI/ML feature developer agent."""
    
    def __init__(self):
        super().__init__(
            name="FeatureAI",
            role="Feature/Innovation Agent - AI/ML models, automation, predictions",
            model_type="coding"
        )
        self.system_prompt += """
You implement AI/ML features and automation:
1. Machine learning models
2. Data processing pipelines
3. Prediction services
4. Automation scripts
5. Integration with core application

Generate production-ready ML code with proper structure.
"""
    
    def generate_features(self, requirements: Dict, architecture: Dict) -> Dict:
        """Generate AI/ML feature code."""
        prompt = f"""Create AI/ML features for:

Requirements: {json.dumps(requirements, indent=2)}

Generate:
1. ML model implementation (if applicable)
2. Data processing pipelines
3. Prediction/inference service
4. Automation scripts
5. Feature configuration

Output as JSON with file paths as keys and code as values.
"""
        response = self._call_llm(prompt, max_tokens=6000)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"feature_code": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_features(context.requirements, context.architecture)


class PresentationAI(BaseAgent):
    """Presentation and documentation agent."""
    
    def __init__(self):
        super().__init__(
            name="PresentationAI",
            role="Presentation Agent - PPT slides, visualizations, documentation",
            model_type="creative"
        )
        self.system_prompt += """
You create professional presentations and documentation:
1. PowerPoint slide content
2. README and documentation
3. Architecture diagrams descriptions
4. Demo flow scripts
5. Visual mockup descriptions

Focus on clear, compelling content for evaluators.
"""
    
    def generate_presentation(self, context: Dict) -> Dict:
        """Generate presentation content."""
        prompt = f"""Create presentation materials for this project:

{json.dumps(context, indent=2)}

Generate:
1. README.md - Complete project documentation
2. PRESENTATION.md - Slide-by-slide content for a 10-slide pitch
3. DEMO_SCRIPT.md - Step-by-step demo walkthrough
4. ARCHITECTURE.md - Technical architecture documentation

Output as JSON with file names as keys and markdown content as values.
"""
        response = self._call_llm(prompt, max_tokens=8000)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"presentation_content": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_presentation({
            "name": context.project_name,
            "description": context.description,
            "requirements": context.requirements,
            "architecture": context.architecture
        })


class IntegrationAI(BaseAgent):
    """Integration and testing agent."""
    
    def __init__(self):
        super().__init__(
            name="IntegrationAI",
            role="Integration & Testing Agent - QA, testing, module integration"
        )
        self.system_prompt += """
You handle testing and integration:
1. Unit test generation
2. Integration test scenarios
3. API testing scripts
4. Test data fixtures
5. CI/CD pipeline configuration

Generate comprehensive test suites.
"""
    
    def generate_tests(self, code_modules: Dict) -> Dict:
        """Generate test suites."""
        prompt = f"""Create comprehensive tests for these modules:

{json.dumps(list(code_modules.keys()), indent=2)}

Generate:
1. Unit tests for each module
2. Integration tests for API endpoints
3. Test fixtures and mock data
4. pytest configuration
5. GitHub Actions CI workflow

Output as JSON with test file paths and content.
"""
        response = self._call_llm(prompt, max_tokens=6000)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"tests": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_tests({"files": context.files_created})


class EvaluationAI(BaseAgent):
    """Evaluation and metrics agent."""
    
    def __init__(self):
        super().__init__(
            name="EvaluationAI",
            role="Metrics & Evaluation Agent - KPIs, scoring, performance analysis",
            model_type="analysis"
        )
        self.system_prompt += """
You analyze and evaluate projects:
1. KPI definition and tracking
2. Scoring predictions
3. Improvement suggestions
4. Benchmark comparisons
5. Quality metrics

Provide actionable insights.
"""
    
    def evaluate_project(self, context: Dict) -> Dict:
        """Evaluate project and predict scoring."""
        prompt = f"""Evaluate this project:

{json.dumps(context, indent=2)}

Provide:
1. Completeness score (0-100)
2. Innovation score (0-100)
3. Documentation quality (0-100)
4. Demo readiness (0-100)
5. Overall predicted score
6. Top 5 improvement suggestions
7. Strengths and weaknesses

Output as JSON.
"""
        response = self._call_llm(prompt)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"evaluation": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.evaluate_project({
            "name": context.project_name,
            "files_created": context.files_created,
            "requirements": context.requirements
        })


class DevOpsAI(BaseAgent):
    """DevOps and deployment agent."""
    
    def __init__(self):
        super().__init__(
            name="DevOpsAI",
            role="DevOps Agent - Deployment, CI/CD, monitoring, infrastructure"
        )
        self.system_prompt += """
You handle deployment and infrastructure:
1. Docker configurations
2. Kubernetes manifests
3. CI/CD pipelines
4. Monitoring setup
5. Environment configuration

Generate production-ready DevOps configurations.
"""
    
    def generate_devops(self, architecture: Dict) -> Dict:
        """Generate DevOps configurations."""
        prompt = f"""Create DevOps configurations for:

{json.dumps(architecture, indent=2)}

Generate:
1. Dockerfile (multi-stage, production-ready)
2. docker-compose.yml (development)
3. docker-compose.prod.yml (production)
4. .github/workflows/ci.yml (CI pipeline)
5. .github/workflows/deploy.yml (CD pipeline)
6. kubernetes/ manifests (if applicable)
7. .env.example

Output as JSON with file paths and content.
"""
        response = self._call_llm(prompt, max_tokens=6000)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"devops_config": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_devops(context.architecture)


class SecurityAI(BaseAgent):
    """Security and compliance agent."""
    
    def __init__(self):
        super().__init__(
            name="SecurityAI",
            role="Security Agent - Risk assessment, compliance, security hardening"
        )
        self.system_prompt += """
You handle security and compliance:
1. Security assessment
2. Vulnerability identification
3. Security configurations
4. Compliance checklists
5. Risk mitigation strategies

Focus on OWASP, data protection, and best practices.
"""
    
    def assess_security(self, architecture: Dict, code_files: List[str]) -> Dict:
        """Assess security and generate recommendations."""
        prompt = f"""Perform security assessment:

Architecture: {json.dumps(architecture, indent=2)}
Code files: {json.dumps(code_files)}

Provide:
1. Security risk assessment
2. Vulnerability checklist
3. Security configurations to add
4. Compliance recommendations
5. Incident response plan outline

Output as JSON.
"""
        response = self._call_llm(prompt)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"security_assessment": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.assess_security(context.architecture, context.files_created)


class FeedbackLoopAI(BaseAgent):
    """Continuous improvement agent."""
    
    def __init__(self):
        super().__init__(
            name="FeedbackLoopAI",
            role="Continuous Improvement Agent - Feedback processing, refinement"
        )
        self.system_prompt += """
You handle continuous improvement:
1. Process feedback from evaluations
2. Identify improvement areas
3. Generate refined prompts
4. Update recommendations
5. Track improvement metrics
"""
    
    def process_feedback(self, evaluation: Dict, context: Dict) -> Dict:
        """Process feedback and suggest improvements."""
        prompt = f"""Process this evaluation and suggest improvements:

Evaluation: {json.dumps(evaluation, indent=2)}
Context: {json.dumps(context, indent=2)}

Provide:
1. Priority improvements (ranked)
2. Specific code changes needed
3. Documentation updates
4. New features to add
5. Refined prompts for other agents

Output as JSON.
"""
        response = self._call_llm(prompt)
        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            return json.loads(response)
        except:
            return {"improvements": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.process_feedback(context.metrics, {
            "name": context.project_name,
            "files": context.files_created
        })


# ══════════════════════════════════════════════════════════════════════════════
# PROJECT FACTORY
# ══════════════════════════════════════════════════════════════════════════════

class ProjectFactory:
    """Creates standardized project structures."""
    
    STRUCTURE = {
        "01_Proposal.md": "Project proposal and overview",
        "02_Project_Report.md": "Detailed project report",
        "03_Architecture.md": "System architecture documentation",
        "04_SRS.md": "Software Requirements Specification",
        "05_PPT.md": "Presentation slide content",
        "06_Demo.md": "Demo script and walkthrough",
        "07_Testing.md": "Test cases and results",
        "08_Risk_and_Security.md": "Risk assessment and security",
        "09_Assets/Diagrams/.gitkeep": "",
        "09_Assets/DataSets/.gitkeep": "",
        "09_Assets/Screenshots/.gitkeep": "",
        "10_Code/Frontend/.gitkeep": "",
        "10_Code/Backend/.gitkeep": "",
        "10_Code/AI_Agents/.gitkeep": "",
        "10_Code/Scripts/.gitkeep": "",
        "README.md": "Project README",
        ".project-config.json": "Project configuration",
    }
    
    @classmethod
    def create_structure(cls, project_dir: str) -> List[str]:
        """Create the standard project structure."""
        created = []
        for path, description in cls.STRUCTURE.items():
            full_path = os.path.join(project_dir, path)
            dir_path = os.path.dirname(full_path)
            
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            
            if not os.path.exists(full_path):
                with open(full_path, 'w', encoding='utf-8') as f:
                    if path.endswith('.md'):
                        f.write(f"# {os.path.basename(path).replace('.md', '').replace('_', ' ')}\n\n")
                        f.write(f"> {description}\n\n")
                        f.write("*Auto-generated by AI Project Brigade*\n")
                    elif path.endswith('.json'):
                        f.write("{}")
                    else:
                        f.write("")
                created.append(path)
        
        return created


# ══════════════════════════════════════════════════════════════════════════════
# ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

# Import v4 capabilities
try:
    from git_ops import GitOps
    from repair import CodeHealer
    V4_MODE = True
except ImportError:
    V4_MODE = False

class BrigadeOrchestrator:
    """
    Main orchestrator that coordinates all AI agents.
    Manages task queue, dependencies, and execution flow.
    """
    
    def __init__(self):
        # Load enhanced configuration if available
        self.profile_name = "web_app"
        self.config = {}
        self.healer = CodeHealer() if V4_MODE else None
        
        # Initialize default agents
        self.agents = {
            "ProjectLeadAI": ProjectLeadAI(),
            "TechArchitectAI": TechArchitectAI(),
            "DataEngineerAI": DataEngineerAI(),
            "FrontendAI": FrontendAI(),
            "BackendAI": BackendAI(),
            "FeatureAI": FeatureAI(),
            "PresentationAI": PresentationAI(),
            "IntegrationAI": IntegrationAI(),
            "EvaluationAI": EvaluationAI(),
            "DevOpsAI": DevOpsAI(),
            "SecurityAI": SecurityAI(),
            "FeedbackLoopAI": FeedbackLoopAI(),
        }
        
        # Load plugin agents
        if ENHANCED_MODE:
            try:
                load_plugins()
                plugin_agents = get_all_agents()
                for name, agent_cls in plugin_agents.items():
                    if name not in self.agents:
                        # Instantiate plugin agent
                        try:
                            self.agents[name] = agent_cls()
                            print(f"🔌 Loaded plugin agent: {name}")
                        except Exception as e:
                            print(f"⚠️  Failed to load plugin {name}: {e}")
            except Exception as e:
                print(f"⚠️  Plugin system error: {e}")

        self.task_queue = queue.Queue()
        self.completed_tasks = {}
        self.logger = logging.getLogger("Orchestrator")
    
    def create_project(self, description: str, project_name: str = None, profile_name: str = None) -> ProjectContext:
        """Create a complete project using all agents."""
        
        print("\n" + "═" * 80)
        print("🏭 AI PROJECT BRIGADE - MULTI-AGENT SYSTEM v4.0 (Autonomous)")
        print("═" * 80)
        
        # Determine profile
        if ENHANCED_MODE:
            if not profile_name:
                print("\n🧠 Analyzing project type...")
                profile_name = suggest_profile(description)
            
            profile = get_profile(profile_name)
            self.profile_name = profile_name
            print(f"🎯 Selected Profile: {profile.name}")
            print(f"   Type: {profile.project_type.value}")
            print(f"   Complexity: {profile.estimated_complexity}")
        
        # Initialize project context
        if not project_name:
            project_name = self._extract_name(description)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = os.path.join(PROJECTS_DIR, f"{project_name}_{timestamp}")
        os.makedirs(project_dir, exist_ok=True)
        
        context = ProjectContext(
            project_name=project_name,
            project_dir=project_dir,
            description=description
        )
        
        # Initialize Git Repo (v4)
        if V4_MODE:
            GitOps.init_repo(project_dir)
            tech_stack = []
            if ENHANCED_MODE and profile:
                tech_stack.extend([profile.tech_stack.frontend, profile.tech_stack.backend])
            GitOps.create_gitignore(project_dir, tech_stack)
            GitOps.commit(project_dir, "feat: Update .gitignore")

        # Run pre-generation hooks/validation
        if ENHANCED_MODE:
            print("\n🔍 Running pre-generation checks...")
            val_result = run_validation("pre-check", "basic") # dummy path for pre-check
            run_hooks("pre_generation", context)

        print(f"\n📋 Project: {project_name}")
        print(f"📁 Location: {project_dir}")
        print("-" * 80)
        
        # Phase 1: Create project structure
        print("\n🏗️  PHASE 1: Creating Project Structure")
        self._phase_indicator(1, 7)
        
        # Use profile-specific structure if available
        if ENHANCED_MODE and profile:
            profile_structure = {}
            for item in profile.structure:
                # Map to description based on extension
                desc = "Source file"
                if item.endswith("/"): desc = "Directory"
                elif item.endswith(".md"): desc = "Documentation"
                elif item.endswith(".json"): desc = "Configuration"
                profile_structure[item] = desc
            
            # Merge with default project factory structure for core files
            structure_to_create = profile.structure
        else:
             # Fallback to default
            structure_to_create = ProjectFactory.STRUCTURE.keys()

        # We need to adapt ProjectFactory to take list or we just create default then add profile specific
        context.files_created.extend(ProjectFactory.create_structure(project_dir))
        
        # Create profile specific directories/files if they aren't in default
        if ENHANCED_MODE and profile:
            for item in profile.structure:
                full_path = os.path.join(project_dir, item)
                if item.endswith("/"):
                    os.makedirs(full_path, exist_ok=True)
                else:
                    if not os.path.exists(full_path):
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        with open(full_path, "w") as f: f.write("")
                        context.files_created.append(item)
            print(f"   ✅ Created {len(context.files_created)} files (Profile: {profile.name})")
        else:
            print(f"   ✅ Created {len(context.files_created)} template files")
        
        if V4_MODE:
            GitOps.commit(project_dir, "feat: Initial Project Structure")

        # Phase 2: Requirements Analysis (ProjectLeadAI)
        print("\n🎯 PHASE 2: Analyzing Requirements")
        self._phase_indicator(2, 7)
        req_prompt = description
        if ENHANCED_MODE and profile:
            req_prompt = f"Project Type: {profile.name}\nTech Stack: {profile.tech_stack.to_dict()}\n\n{description}"
            
        context.requirements = self.agents["ProjectLeadAI"].analyze_requirements(req_prompt)
        self._save_to_file(project_dir, "01_Proposal.md", self._format_proposal(context))
        print("   ✅ Requirements analyzed, tasks assigned")
        
        if V4_MODE:
            GitOps.commit(project_dir, "docs: Requirements and Proposal")

        # Phase 3: Architecture Design (TechArchitectAI)
        print("\n🏛️  PHASE 3: Designing Architecture")
        self._phase_indicator(3, 7)
        context.architecture = self.agents["TechArchitectAI"].design_architecture(context.requirements)
        self._save_to_file(project_dir, "03_Architecture.md", self._format_architecture(context))
        print("   ✅ Architecture designed")
        
        if V4_MODE:
            GitOps.commit(project_dir, "arch: System Architecture Design")

        # Phase 4: Code Generation
        print("\n💻 PHASE 4: Generating Code")
        self._phase_indicator(4, 7)
        
        # Determine active agents based on profile if available
        active_agents = set(self.agents.keys())
        if ENHANCED_MODE and profile:
            active_agents = set(profile.agents)
            # Ensure core coding agents are active if needed but respecting profile
            # Actually, let's just use the profile's agent list + allow fallbacks
        
        # Generate backend
        if "BackendAI" in active_agents:
            print("   📦 Backend generation...", end=" ", flush=True)
            backend_code = self.agents["BackendAI"].generate_backend(context.requirements, context.architecture)
            files_created = self._save_code_files(project_dir, backend_code, "10_Code/Backend")
            context.files_created.extend(files_created)
            print(f"✅ ({len(files_created)} files)")
        
        if V4_MODE:
            GitOps.commit(project_dir, "feat: Backend Implementation")

        # Generate frontend
        if "FrontendAI" in active_agents:
            print("   🎨 Frontend generation...", end=" ", flush=True)
            frontend_code = self.agents["FrontendAI"].generate_frontend(context.requirements, context.architecture)
            files_created = self._save_code_files(project_dir, frontend_code, "10_Code/Frontend")
            context.files_created.extend(files_created)
            print(f"✅ ({len(files_created)} files)")
        
        if V4_MODE:
             GitOps.commit(project_dir, "feat: Frontend Implementation")

        # Generate data layer
        if "DataEngineerAI" in active_agents:
            print("   🗄️  Data layer generation...", end=" ", flush=True)
            data_code = self.agents["DataEngineerAI"].generate_data_layer(context.architecture)
            files_created = self._save_code_files(project_dir, data_code, "10_Code/Backend/data")
            context.files_created.extend(files_created)
            print(f"✅ ({len(files_created)} files)")
        
        # Phase 5: DevOps & Testing
        print("\n🔧 PHASE 5: DevOps & Testing")
        self._phase_indicator(5, 7)
        
        if "DevOpsAI" in active_agents:
            print("   🐳 DevOps configuration...", end=" ", flush=True)
            devops = self.agents["DevOpsAI"].generate_devops(context.architecture)
            files_created = self._save_code_files(project_dir, devops, "")
            context.files_created.extend(files_created)
            print(f"✅ ({len(files_created)} files)")
        
        if "IntegrationAI" in active_agents:
            print("   🧪 Test generation...", end=" ", flush=True)
            tests = self.agents["IntegrationAI"].generate_tests({"files": context.files_created})
            files_created = self._save_code_files(project_dir, tests, "10_Code/Tests")
            context.files_created.extend(files_created)
            print(f"✅ ({len(files_created)} files)")
        
        if V4_MODE:
            GitOps.commit(project_dir, "chore: DevOps and Tests")

        # Phase 6: Documentation & Presentation
        print("\n📚 PHASE 6: Documentation & Presentation")
        self._phase_indicator(6, 7)
        
        if "PresentationAI" in active_agents:
            print("   📝 Generating documentation...", end=" ", flush=True)
            presentation = self.agents["PresentationAI"].generate_presentation({
                "name": context.project_name,
                "description": context.description,
                "requirements": context.requirements,
                "architecture": context.architecture
            })
            files_created = self._save_code_files(project_dir, presentation, "")
            context.files_created.extend(files_created)
            print(f"✅ ({len(files_created)} files)")
        
        # Security assessment
        if "SecurityAI" in active_agents:
            print("   🔒 Security assessment...", end=" ", flush=True)
            security = self.agents["SecurityAI"].assess_security(context.architecture, context.files_created)
            self._save_to_file(project_dir, "08_Risk_and_Security.md", self._format_security(security))
            print("✅")
        
        # Phase 7: Evaluation
        print("\n📊 PHASE 7: Project Evaluation")
        self._phase_indicator(7, 7)
        
        if "EvaluationAI" in active_agents:
            print("   📈 Evaluating project...", end=" ", flush=True)
            context.metrics = self.agents["EvaluationAI"].evaluate_project({
                "name": context.project_name,
                "files_created": context.files_created,
                "requirements": context.requirements,
                "architecture": context.architecture
            })
            print("✅")
        
        # Run plugin agents
        if ENHANCED_MODE:
             for name, agent in self.agents.items():
                 # Run custom agents that aren't in the standard list
                 if name not in ["ProjectLeadAI", "TechArchitectAI", "DataEngineerAI", "FrontendAI", 
                                "BackendAI", "FeatureAI", "PresentationAI", "IntegrationAI", 
                                "EvaluationAI", "DevOpsAI", "SecurityAI", "FeedbackLoopAI"]:
                     print(f"   🔌 Running plugin: {name}...", end=" ", flush=True)
                     try:
                         # Plugins might have different signatures, best effort
                         if hasattr(agent, 'run'):
                            agent.run(context.requirements, context)
                         print("✅")
                     except Exception as e:
                         print(f"❌ ({e})")

        # Save final project config
        config = {
            "project_name": context.project_name,
            "profile": self.profile_name,
            "created_at": datetime.now().isoformat(),
            "files_created": context.files_created,
            "requirements": context.requirements,
            "metrics": context.metrics
        }
        with open(os.path.join(project_dir, ".project-config.json"), 'w') as f:
            json.dump(config, f, indent=2)
        
        context.status = "completed"
        
        # Run post-generation validation and hooks
        if ENHANCED_MODE:
            print("\n🔍 Running final validation...", end=" ", flush=True)
            val_report = run_validation(project_dir, "standard")
            print(f" Score: {val_report['score']:.1f}%")
            if not val_report['passed_gate']:
                print("   ⚠️  Quality gate failed. Check validation report.")
            
            run_hooks("post_generation", context)

        if V4_MODE:
            GitOps.commit(project_dir, "chore: Final project generation")

        # Print summary
        self._print_summary(context)
        
        return context

    def _save_code_files(self, project_dir: str, code_dict: Dict, subdirectory: str) -> List[str]:
        """Save generated code files."""
        created = []
        if isinstance(code_dict, dict):
            for filepath, content in code_dict.items():
                if isinstance(content, str) and len(content) > 10:
                    if subdirectory:
                        full_path = os.path.join(project_dir, subdirectory, filepath)
                    else:
                        full_path = os.path.join(project_dir, filepath)
                    
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Clean content if it has markdown code blocks
                    if content.strip().startswith("```"):
                        lines = content.strip().split("\n")
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].strip() == "```":
                            lines = lines[:-1]
                        content = "\n".join(lines)
                    
                    # V4: Auto-Healing
                    if V4_MODE and self.healer:
                        content = self.healer.process_file(full_path, content)

                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created.append(filepath)
        return created
    
    def _extract_name(self, description: str) -> str:
        """Extract project name from description."""
        words = description.lower().split()[:4]
        name = "-".join(w for w in words if w.isalnum())
        return name[:30] or "new-project"
    
    def _phase_indicator(self, current: int, total: int):
        """Print phase progress indicator."""
        progress = "█" * current + "░" * (total - current)
        print(f"   [{progress}] Phase {current}/{total}")
    
    def _save_to_file(self, project_dir: str, filename: str, content: str):
        """Save content to a file."""
        filepath = os.path.join(project_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _save_code_files(self, project_dir: str, code_dict: Dict, subdirectory: str) -> List[str]:
        """Save generated code files."""
        created = []
        if isinstance(code_dict, dict):
            for filepath, content in code_dict.items():
                if isinstance(content, str) and len(content) > 10:
                    if subdirectory:
                        full_path = os.path.join(project_dir, subdirectory, filepath)
                    else:
                        full_path = os.path.join(project_dir, filepath)
                    
                    os.makedirs(os.path.dirname(full_path), exist_ok=True)
                    
                    # Clean content if it has markdown code blocks
                    if content.strip().startswith("```"):
                        lines = content.strip().split("\n")
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].strip() == "```":
                            lines = lines[:-1]
                        content = "\n".join(lines)
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    created.append(filepath)
        return created
    
    def _format_proposal(self, context: ProjectContext) -> str:
        """Format proposal document."""
        req = context.requirements
        return f"""# Project Proposal: {context.project_name}

## Executive Summary
{req.get('summary', context.description)}

## Project Goals
{chr(10).join('- ' + g for g in req.get('goals', ['Define project goals']))}

## Scope
### In Scope
{chr(10).join('- ' + s for s in req.get('scope', {}).get('in_scope', []))}

### Out of Scope
{chr(10).join('- ' + s for s in req.get('scope', {}).get('out_of_scope', []))}

## Technology Stack
{json.dumps(req.get('tech_stack', {}), indent=2)}

## Milestones
{json.dumps(req.get('milestones', []), indent=2)}

---
*Generated by AI Project Brigade*
"""
    
    def _format_architecture(self, context: ProjectContext) -> str:
        """Format architecture document."""
        arch = context.architecture
        return f"""# System Architecture: {context.project_name}

## Overview
{arch.get('architecture_description', json.dumps(arch, indent=2))}

## Diagram
```
{arch.get('diagram', 'See architecture details above')}
```

## Modules
{json.dumps(arch.get('modules', {}), indent=2)}

## Database Schema
{json.dumps(arch.get('database', {}), indent=2)}

## API Endpoints
{json.dumps(arch.get('api_endpoints', []), indent=2)}

---
*Generated by AI Project Brigade*
"""
    
    def _format_security(self, security: Dict) -> str:
        """Format security document."""
        return f"""# Risk & Security Assessment

## Security Assessment
{json.dumps(security, indent=2)}

---
*Generated by AI Project Brigade*
"""
    
    def _print_summary(self, context: ProjectContext):
        """Print project summary."""
        metrics = context.metrics if isinstance(context.metrics, dict) else {}
        
        print("\n" + "═" * 80)
        print("🎉 PROJECT CREATION COMPLETE!")
        print("═" * 80)
        
        print(f"\n📋 Project: {context.project_name}")
        print(f"📁 Location: {context.project_dir}")
        print(f"📄 Files Created: {len(context.files_created)}")
        
        if metrics:
            print("\n📊 Evaluation Scores:")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    bar = "█" * (int(value) // 10) + "░" * (10 - int(value) // 10)
                    print(f"   {key}: [{bar}] {value}")
        
        print("\n📂 Project Structure:")
        print("   " + context.project_dir)
        for f in context.files_created[:10]:
            print(f"   ├── {f}")
        if len(context.files_created) > 10:
            print(f"   └── ... and {len(context.files_created) - 10} more files")
        
        print("\n" + "═" * 80)
        print("🚀 Next Steps:")
        print(f"   1. cd \"{context.project_dir}\"")
        print("   2. Review generated code and documentation")
        print("   3. Run: docker-compose up --build")
        print("   4. Access the application and customize as needed")
        print("═" * 80 + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

def print_banner():
    """Print the system banner."""
    print("""
╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                                  ║
║     █████╗ ██╗    ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗                    ║
║    ██╔══██╗██║    ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝                    ║
║    ███████║██║    ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║                       ║
║    ██╔══██║██║    ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║                       ║
║    ██║  ██║██║    ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║                       ║
║    ╚═╝  ╚═╝╚═╝    ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝                       ║
║                                                                                                  ║
║    ██████╗ ██████╗ ██╗ ██████╗  █████╗ ██████╗ ███████╗    ██╗   ██╗██████╗    ██████╗          ║
║    ██╔══██╗██╔══██╗██║██╔════╝ ██╔══██╗██╔══██╗██╔════╝    ██║   ██║╚════██╗  ██╔═████╗         ║
║    ██████╔╝██████╔╝██║██║  ███╗███████║██║  ██║█████╗      ██║   ██║ █████╔╝  ██║██╔██║         ║
║    ██╔══██╗██╔══██╗██║██║   ██║██╔══██║██║  ██║██╔══╝      ╚██╗ ██╔╝ ╚═══██╗  ████╔╝██║         ║
║    ██████╔╝██║  ██║██║╚██████╔╝██║  ██║██████╔╝███████╗     ╚████╔╝ ██████╔╝  ╚██████╔╝         ║
║    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝      ╚═══╝  ╚═════╝    ╚═════╝          ║
║                                                                                                  ║
║                     🏭 Multi-Agent System for Autonomous Project Development                     ║
║                                                                                                  ║
║    Agents: ProjectLead | TechArchitect | DataEngineer | Frontend | Backend | Feature            ║
║            Presentation | Integration | Evaluation | DevOps | Security | FeedbackLoop           ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)


def show_agents():
    """Display agent roster."""
    agents = [
        ("🎯", "ProjectLeadAI", "Coordinator, task assignment, milestones"),
        ("🏛️", "TechArchitectAI", "System design, architecture, module specs"),
        ("🗄️", "DataEngineerAI", "Data pipelines, cleaning, API integration"),
        ("🎨", "FrontendAI", "UI/UX, dashboards, responsive components"),
        ("⚙️", "BackendAI", "APIs, business logic, databases"),
        ("🧠", "FeatureAI", "AI/ML models, automation, predictions"),
        ("📊", "PresentationAI", "PPT, documentation, visualizations"),
        ("🧪", "IntegrationAI", "Testing, QA, module integration"),
        ("📈", "EvaluationAI", "KPIs, scoring, metrics analysis"),
        ("🐳", "DevOpsAI", "Deployment, CI/CD, monitoring"),
        ("🔒", "SecurityAI", "Risk assessment, compliance, security"),
        ("🔄", "FeedbackLoopAI", "Continuous improvement, refinement"),
    ]
    
    print("\n🤖 AI AGENT ROSTER")
    print("═" * 60)
    for icon, name, role in agents:
        print(f"   {icon} {name:20} │ {role}")
    print("═" * 60)


def interactive_mode():
    """Run interactive CLI mode."""
    print_banner()
    show_agents()
    
    print("\n💡 Welcome to AI Project Brigade! (Enhanced Mode)")
    print("   I'll deploy my team of AI agents to build your project.\n")
    
    while True:
        print("─" * 60)
        print("\n🎯 Options:")
        print("   1. Create a new project")
        print("   2. Browse Project Profiles")
        print("   3. Show agent roster")
        print("   4. Run Validation on existing project")
        print("   5. Exit")
        
        choice = input("\n>>> ").strip()
        
        if choice == "1":
            print("\n📝 Describe your project in detail:")
            print("   (Include features, tech preferences, target audience, etc.)")
            print("   (Press Enter twice to submit)\n")
            
            lines = []
            while True:
                line = input()
                if line:
                    lines.append(line)
                else:
                    if lines:
                        break
                    print("   [Please enter a description]")
            
            description = "\n".join(lines)
            
            # Optional: custom project name
            print("\n📛 Project name (leave empty for auto-generated):")
            project_name = input(">>> ").strip() or None
            
            # Optional: Select Profile
            profile_name = None
            if ENHANCED_MODE:
                print("\n🧠 Auto-detect project profile? (y/n)")
                if input(">>> ").lower().startswith('n'):
                    print("\nAvailable Profiles:")
                    profiles = list_profiles()
                    for p in profiles:
                        print(f" - {p}")
                    print("\nEnter profile name:")
                    profile_name = input(">>> ").strip()
            
            # Create project
            orchestrator = BrigadeOrchestrator()
            result = orchestrator.create_project(description, project_name, profile_name)
            
        elif choice == "2":
            if ENHANCED_MODE:
                print("\n📁 Available Project Profiles:")
                profiles = list_profiles()
                for p_name in profiles:
                    p = get_profile(p_name)
                    print(f"\n🔹 {p.name} ({p_name})")
                    print(f"   {p.description}")
                    print(f"   Type: {p.project_type.value}")
                    print(f"   Tech Stack: {p.tech_stack.frontend} + {p.tech_stack.backend}")
            else:
                print("Profiles not available in standard mode.")

        elif choice == "3":
            show_agents()
            if ENHANCED_MODE:
                print("\n🔌 Loaded Plugins:")
                try:
                    plugins = get_all_agents()
                    for name in plugins:
                         if name not in ["ProjectLeadAI", "TechArchitectAI", "DataEngineerAI", "FrontendAI", 
                                        "BackendAI", "FeatureAI", "PresentationAI", "IntegrationAI", 
                                        "EvaluationAI", "DevOpsAI", "SecurityAI", "FeedbackLoopAI"]:
                             print(f"   ✨ {name}")
                except:
                    print("   None")

        elif choice == "4":
            if ENHANCED_MODE:
                print("\nEnter project path:")
                path = input(">>> ").strip()
                if os.path.exists(path):
                    print(f"\n🔍 Validating {path}...")
                    try:
                        report = run_validation(path)
                        print(f"Score: {report['score']}%")
                        print(f"Passed: {report['passed_gate']}")
                        print(f"Report saved to {report['report_path']}")
                    except Exception as e:
                        print(f"Error: {e}")
                else:
                    print("Path not found.")
            else:
                print("Validation not available in standard mode.")

        elif choice == "5":
            print("\n👋 Goodbye from the AI Brigade!")
            break
        else:
            print("Invalid option")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == "--agents":
            show_agents()
        elif sys.argv[1] == "--validate" and len(sys.argv) > 2:
            if ENHANCED_MODE:
                 run_validation(sys.argv[2])
            else:
                print("Validation not available.")
        elif sys.argv[1] == "--profiles":
             if ENHANCED_MODE:
                print(list_profiles())
             else: 
                print("Profiles not available.")
        else:
            # Parse arguments simply
            description = ""
            profile = None
            
            args = sys.argv[1:]
            if "--profile" in args:
                p_idx = args.index("--profile")
                if p_idx + 1 < len(args):
                    profile = args[p_idx+1]
                    # Remove from description
                    del args[p_idx:p_idx+2]
            
            description = " ".join(args)
            
            orchestrator = BrigadeOrchestrator()
            orchestrator.create_project(description, profile_name=profile)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
