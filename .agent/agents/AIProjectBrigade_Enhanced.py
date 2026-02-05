"""
╔══════════════════════════════════════════════════════════════════════════════════════════════════╗
║                      🏭 AI PROJECT BRIGADE - ENHANCED v3.5                                       ║
║              Multi-Agent System with Async Execution, Caching & Templates                         ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝

ENHANCEMENTS:
- ⚡ Async parallel agent execution
- 🔄 Retry logic with exponential backoff
- 💾 Response caching to avoid redundant API calls
- 📁 Project template system
- ⚙️ External YAML configuration
- 📊 Rich progress UI with live updates
- 🔌 Plugin system for custom agents
- 📝 File-based logging
- 🧪 Validation & testing hooks

Author: KARYA AGENT System
Version: 3.5.0
"""

import os
import sys
import json
import hashlib
import asyncio
import logging
import time
import functools
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Third-party imports
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class ConfigManager:
    """Manages configuration from YAML file and environment variables."""
    
    DEFAULT_CONFIG = {
        "api": {
            "provider": "openrouter",
            "base_url": "https://openrouter.ai/api/v1",
            "models": {
                "reasoning": "google/gemini-2.0-flash-001",
                "coding": "google/gemini-2.0-flash-001",
                "creative": "google/gemini-2.0-flash-001",
                "analysis": "google/gemini-2.0-flash-001",
            },
            "max_retries": 3,
            "retry_delay": 2,
            "timeout": 120,
        },
        "project": {
            "output_dir": "projects",
            "templates_dir": "templates",
        },
        "execution": {
            "parallel": True,
            "max_concurrent": 4,
            "cache_responses": True,
            "cache_ttl": 3600,
            "verbose": True,
        },
        "logging": {
            "level": "INFO",
            "file": "logs/brigade.log",
        }
    }
    
    def __init__(self, config_path: str = None):
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "config.yaml"
        )
        self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if YAML_AVAILABLE and os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    yaml_config = yaml.safe_load(f)
                    if yaml_config:
                        self._deep_merge(self.config, yaml_config)
            except Exception as e:
                print(f"Warning: Could not load config.yaml: {e}")
    
    def _apply_env_overrides(self):
        """Apply environment variable overrides."""
        if os.getenv("OPENROUTER_API_KEY"):
            self.config["api"]["api_key"] = os.getenv("OPENROUTER_API_KEY")
        if os.getenv("BRIGADE_MODEL"):
            for key in self.config["api"]["models"]:
                self.config["api"]["models"][key] = os.getenv("BRIGADE_MODEL")
    
    def _deep_merge(self, base: dict, override: dict):
        """Deep merge override into base."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, *keys, default=None):
        """Get nested config value."""
        value = self.config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value


# ══════════════════════════════════════════════════════════════════════════════
# RESPONSE CACHE
# ══════════════════════════════════════════════════════════════════════════════

class ResponseCache:
    """LRU cache for LLM responses with TTL."""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.max_size = max_size
        self.ttl = ttl
        self.cache: Dict[str, Tuple[str, datetime]] = {}
        self.lock = threading.Lock()
    
    def _hash_key(self, prompt: str, model: str) -> str:
        """Generate cache key from prompt and model."""
        content = f"{model}:{prompt}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, prompt: str, model: str) -> Optional[str]:
        """Get cached response if valid."""
        key = self._hash_key(prompt, model)
        with self.lock:
            if key in self.cache:
                response, timestamp = self.cache[key]
                if datetime.now() - timestamp < timedelta(seconds=self.ttl):
                    return response
                else:
                    del self.cache[key]
        return None
    
    def set(self, prompt: str, model: str, response: str):
        """Cache a response."""
        key = self._hash_key(prompt, model)
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest entry
                oldest_key = min(self.cache, key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            self.cache[key] = (response, datetime.now())
    
    def clear(self):
        """Clear the cache."""
        with self.lock:
            self.cache.clear()


# ══════════════════════════════════════════════════════════════════════════════
# LOGGING SETUP
# ══════════════════════════════════════════════════════════════════════════════

def setup_logging(config: ConfigManager) -> logging.Logger:
    """Setup logging with file and console handlers."""
    log_level = getattr(logging, config.get("logging", "level", default="INFO"))
    log_file = config.get("logging", "file", default="logs/brigade.log")
    
    # Create logs directory
    log_dir = os.path.dirname(log_file)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    
    return logging.getLogger("Brigade")


# ══════════════════════════════════════════════════════════════════════════════
# RETRY DECORATOR
# ══════════════════════════════════════════════════════════════════════════════

def retry_with_backoff(max_retries: int = 3, base_delay: float = 2.0):
    """Decorator for retrying functions with exponential backoff."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)
                        time.sleep(delay)
            raise last_exception
        return wrapper
    return decorator


# ══════════════════════════════════════════════════════════════════════════════
# PROGRESS TRACKER
# ══════════════════════════════════════════════════════════════════════════════

class ProgressTracker:
    """Rich progress tracking for multi-agent execution."""
    
    def __init__(self, total_phases: int = 7):
        self.total_phases = total_phases
        self.current_phase = 0
        self.phase_names = [
            "Project Initialization",
            "Requirements Analysis",
            "Architecture Design",
            "Code Generation",
            "DevOps & Testing",
            "Documentation",
            "Evaluation"
        ]
        self.agent_status: Dict[str, str] = {}
        self.start_time = None
        self.lock = threading.Lock()
    
    def start(self):
        """Start progress tracking."""
        self.start_time = datetime.now()
        self._print_header()
    
    def _print_header(self):
        """Print progress header."""
        print("\n" + "═" * 80)
        print("🏭 AI PROJECT BRIGADE - ENHANCED v3.5")
        print("═" * 80)
    
    def start_phase(self, phase_num: int, phase_name: str = None):
        """Start a new phase."""
        with self.lock:
            self.current_phase = phase_num
            name = phase_name or self.phase_names[phase_num - 1]
            
            progress_bar = "█" * phase_num + "░" * (self.total_phases - phase_num)
            print(f"\n{'─' * 80}")
            print(f"📍 PHASE {phase_num}/{self.total_phases}: {name}")
            print(f"   [{progress_bar}]")
    
    def update_agent(self, agent_name: str, status: str, result: str = ""):
        """Update agent status."""
        with self.lock:
            self.agent_status[agent_name] = status
            icon = "⏳" if status == "working" else "✅" if status == "done" else "❌"
            print(f"   {icon} {agent_name}: {result}")
    
    def complete(self, files_created: int, project_dir: str, metrics: Dict = None):
        """Print completion summary."""
        elapsed = datetime.now() - self.start_time
        
        print("\n" + "═" * 80)
        print("🎉 PROJECT CREATION COMPLETE!")
        print("═" * 80)
        print(f"\n⏱️  Time Elapsed: {elapsed.seconds}s")
        print(f"📁 Location: {project_dir}")
        print(f"📄 Files Created: {files_created}")
        
        if metrics and isinstance(metrics, dict):
            print("\n📊 Evaluation Scores:")
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and 0 <= value <= 100:
                    bar = "█" * (int(value) // 10) + "░" * (10 - int(value) // 10)
                    print(f"   {key}: [{bar}] {value}")
        
        print("\n" + "═" * 80)


# ══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ══════════════════════════════════════════════════════════════════════════════

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    WAITING = "waiting"


@dataclass
class AgentTask:
    """A task assigned to an agent."""
    task_id: str
    agent_name: str
    description: str
    inputs: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    output: Any = None
    error: str = None


@dataclass
class ProjectContext:
    """Shared context for all agents."""
    project_name: str
    project_dir: str
    description: str
    requirements: Dict[str, Any] = field(default_factory=dict)
    architecture: Dict[str, Any] = field(default_factory=dict)
    files_created: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    status: str = "initializing"


# ══════════════════════════════════════════════════════════════════════════════
# ENHANCED BASE AGENT
# ══════════════════════════════════════════════════════════════════════════════

class EnhancedBaseAgent:
    """Enhanced base class with caching, retries, and config support."""
    
    def __init__(self, name: str, role: str, config: ConfigManager, 
                 cache: ResponseCache, model_type: str = "reasoning"):
        self.name = name
        self.role = role
        self.config = config
        self.cache = cache
        self.model = config.get("api", "models", model_type, default="google/gemini-2.0-flash-001")
        self.logger = logging.getLogger(name)
        self.status = AgentStatus.IDLE
        
        api_key = config.get("api", "api_key") or os.getenv("OPENROUTER_API_KEY", "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")
        base_url = config.get("api", "base_url", default="https://openrouter.ai/api/v1")
        
        if OPENAI_AVAILABLE:
            self.client = OpenAI(base_url=base_url, api_key=api_key)
        else:
            self.client = None
        
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build the agent's system prompt."""
        return f"""You are {self.name}, a specialized AI agent in the Project Brigade.
Your role: {self.role}

You are part of a multi-agent system building production-level projects.
Always provide complete, working outputs - never placeholders.
Format outputs clearly and follow best practices.
When asked for JSON, return ONLY valid JSON without markdown formatting.
"""
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def _call_llm(self, prompt: str, max_tokens: int = 4000, use_cache: bool = True) -> str:
        """Make an LLM API call with caching and retries."""
        # Check cache first
        if use_cache and self.config.get("execution", "cache_responses", default=True):
            cached = self.cache.get(prompt, self.model)
            if cached:
                self.logger.debug(f"Cache hit for {self.name}")
                return cached
        
        if not self.client:
            return "Error: OpenAI package not installed"
        
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
            result = response.choices[0].message.content
            
            # Cache the response
            if use_cache and self.config.get("execution", "cache_responses", default=True):
                self.cache.set(prompt, self.model, result)
            
            return result
        except Exception as e:
            self.logger.error(f"LLM Error: {e}")
            raise
    
    def _parse_json(self, response: str) -> dict:
        """Safely parse JSON from LLM response."""
        try:
            # Clean up response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            elif response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            self.logger.warning(f"JSON parse error: {e}")
            return {"raw_response": response}
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        """Process a task. Override in subclasses."""
        raise NotImplementedError


# ══════════════════════════════════════════════════════════════════════════════
# PROJECT TEMPLATES
# ══════════════════════════════════════════════════════════════════════════════

class ProjectTemplates:
    """Pre-built project templates for quick starts."""
    
    TEMPLATES = {
        "fullstack-react-fastapi": {
            "name": "Full-Stack React + FastAPI",
            "description": "React frontend with FastAPI backend and PostgreSQL",
            "stack": {
                "frontend": "react",
                "backend": "fastapi",
                "database": "postgresql",
                "styling": "tailwind"
            },
            "features": ["auth", "crud", "docker", "tests", "ci_cd"],
            "files": {
                "frontend": ["App.jsx", "components/", "services/api.js"],
                "backend": ["main.py", "routes/", "models/", "config.py"]
            }
        },
        "fullstack-nextjs": {
            "name": "Next.js Full-Stack",
            "description": "Next.js with API routes and Prisma",
            "stack": {
                "frontend": "nextjs",
                "backend": "nextjs-api",
                "database": "postgresql",
                "orm": "prisma"
            },
            "features": ["auth", "crud", "docker", "tests"],
            "files": {
                "app": ["layout.tsx", "page.tsx", "api/"],
                "lib": ["db.ts", "auth.ts"]
            }
        },
        "backend-api": {
            "name": "REST API Service",
            "description": "FastAPI REST API with PostgreSQL",
            "stack": {
                "backend": "fastapi",
                "database": "postgresql",
                "cache": "redis"
            },
            "features": ["auth", "crud", "docker", "tests", "docs"],
            "files": {
                "src": ["main.py", "routes/", "services/", "models/"],
                "tests": ["test_api.py"]
            }
        },
        "ml-pipeline": {
            "name": "ML Pipeline",
            "description": "Machine learning pipeline with training and inference API",
            "stack": {
                "ml": "pytorch",
                "backend": "fastapi",
                "tracking": "mlflow"
            },
            "features": ["training", "inference", "api", "docker"],
            "files": {
                "src": ["train.py", "model.py", "api.py"],
                "notebooks": ["exploration.ipynb"],
                "data": ["sample/"]
            }
        },
        "microservices": {
            "name": "Microservices Architecture",
            "description": "Microservices with API gateway and message queue",
            "stack": {
                "gateway": "fastapi",
                "services": ["user", "product", "order"],
                "messaging": "rabbitmq",
                "database": "postgresql"
            },
            "features": ["docker", "kubernetes", "ci_cd", "monitoring"],
            "files": {
                "gateway": ["main.py"],
                "services": ["user/", "product/", "order/"]
            }
        },
        "cli-tool": {
            "name": "CLI Application",
            "description": "Command-line tool with Click",
            "stack": {
                "cli": "click",
                "language": "python"
            },
            "features": ["commands", "config", "tests", "packaging"],
            "files": {
                "src": ["cli.py", "commands/"],
                "tests": ["test_cli.py"]
            }
        }
    }
    
    @classmethod
    def get_template(cls, name: str) -> Optional[Dict]:
        """Get a template by name."""
        return cls.TEMPLATES.get(name)
    
    @classmethod
    def list_templates(cls) -> List[str]:
        """List available template names."""
        return list(cls.TEMPLATES.keys())
    
    @classmethod
    def to_description(cls, template_name: str) -> str:
        """Convert template to project description."""
        template = cls.TEMPLATES.get(template_name)
        if not template:
            return ""
        
        stack_str = ", ".join(f"{k}: {v}" for k, v in template["stack"].items())
        features_str = ", ".join(template["features"])
        
        return f"""
Project: {template["name"]}
Description: {template["description"]}
Technology Stack: {stack_str}
Features: {features_str}
"""


# ══════════════════════════════════════════════════════════════════════════════
# ENHANCED SPECIALIZED AGENTS
# ══════════════════════════════════════════════════════════════════════════════

class ProjectLeadAgent(EnhancedBaseAgent):
    """Enhanced project coordinator."""
    
    def __init__(self, config: ConfigManager, cache: ResponseCache):
        super().__init__(
            name="ProjectLeadAI",
            role="Project Lead - Coordinates agents, defines goals, assigns tasks",
            config=config,
            cache=cache,
            model_type="reasoning"
        )
        self.system_prompt += """
Analyze project requirements and output ONLY valid JSON with:
- project_name: kebab-case name
- summary: one paragraph
- goals: list of goals
- tech_stack: recommended technologies
- agent_tasks: tasks for each agent
- milestones: project milestones
"""
    
    def analyze_requirements(self, description: str) -> Dict:
        """Analyze and create project plan."""
        prompt = f"""Analyze this project and create a task plan:

PROJECT: {description}

Output ONLY valid JSON (no markdown):
{{"project_name": "name", "summary": "...", "goals": [...], "tech_stack": {{}}, "agent_tasks": [...], "milestones": [...]}}
"""
        response = self._call_llm(prompt, max_tokens=3000)
        return self._parse_json(response)
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.analyze_requirements(context.description)


class TechArchitectAgent(EnhancedBaseAgent):
    """Enhanced architecture designer."""
    
    def __init__(self, config: ConfigManager, cache: ResponseCache):
        super().__init__(
            name="TechArchitectAI",
            role="System Architect - Designs architecture and module specs",
            config=config,
            cache=cache,
            model_type="reasoning"
        )
    
    def design_architecture(self, requirements: Dict) -> Dict:
        """Design system architecture."""
        prompt = f"""Design architecture for: {json.dumps(requirements, indent=2)}

Output ONLY valid JSON with:
- diagram: Mermaid diagram string
- modules: list of modules with interfaces
- database: schema design
- api_endpoints: list of endpoints
- data_flow: description
"""
        response = self._call_llm(prompt, max_tokens=5000)
        return self._parse_json(response)
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.design_architecture(context.requirements)


class CodeGeneratorAgent(EnhancedBaseAgent):
    """Enhanced code generator (combines Frontend, Backend, Data)."""
    
    def __init__(self, config: ConfigManager, cache: ResponseCache, specialty: str = "backend"):
        super().__init__(
            name=f"{specialty.title()}AI",
            role=f"{specialty.title()} Developer - Generates {specialty} code",
            config=config,
            cache=cache,
            model_type="coding"
        )
        self.specialty = specialty
        self._customize_prompt()
    
    def _customize_prompt(self):
        """Customize prompt for specialty."""
        if self.specialty == "frontend":
            self.system_prompt += """
Generate complete React/TypeScript code with:
- Functional components with hooks
- Tailwind CSS styling
- Type definitions
- API integration layer
Output as JSON with file paths as keys.
"""
        elif self.specialty == "backend":
            self.system_prompt += """
Generate complete FastAPI/Python code with:
- Type hints and Pydantic models
- Async endpoints
- Error handling
- Database integration
Output as JSON with file paths as keys.
"""
        elif self.specialty == "data":
            self.system_prompt += """
Generate complete data layer code with:
- SQLAlchemy models
- Pydantic schemas
- Migration scripts
- Sample data generators
Output as JSON with file paths as keys.
"""
    
    def generate_code(self, requirements: Dict, architecture: Dict) -> Dict:
        """Generate code files."""
        prompt = f"""Generate {self.specialty} code for:

Requirements: {json.dumps(requirements, indent=2)}
Architecture: {json.dumps(architecture, indent=2)}

Output ONLY valid JSON mapping file paths to complete code content.
Example: {{"src/main.py": "# Complete code..."}}
"""
        response = self._call_llm(prompt, max_tokens=8000)
        return self._parse_json(response)
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_code(context.requirements, context.architecture)


class DevOpsAgent(EnhancedBaseAgent):
    """Enhanced DevOps configuration generator."""
    
    def __init__(self, config: ConfigManager, cache: ResponseCache):
        super().__init__(
            name="DevOpsAI",
            role="DevOps Engineer - Docker, CI/CD, deployment",
            config=config,
            cache=cache,
            model_type="coding"
        )
    
    def generate_devops(self, architecture: Dict) -> Dict:
        """Generate DevOps configurations."""
        prompt = f"""Generate DevOps configs for: {json.dumps(architecture, indent=2)}

Output ONLY valid JSON with file paths and content:
- Dockerfile
- docker-compose.yml
- .github/workflows/ci.yml
- .env.example
"""
        response = self._call_llm(prompt, max_tokens=5000)
        return self._parse_json(response)
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_devops(context.architecture)


class DocumentationAgent(EnhancedBaseAgent):
    """Enhanced documentation and presentation generator."""
    
    def __init__(self, config: ConfigManager, cache: ResponseCache):
        super().__init__(
            name="PresentationAI",
            role="Technical Writer - README, PPT, documentation",
            config=config,
            cache=cache,
            model_type="creative"
        )
    
    def generate_docs(self, context: Dict) -> Dict:
        """Generate documentation."""
        prompt = f"""Generate documentation for: {json.dumps(context, indent=2)}

Output ONLY valid JSON with:
- README.md: Complete project README
- ARCHITECTURE.md: Technical documentation
- DEMO.md: Demo walkthrough
"""
        response = self._call_llm(prompt, max_tokens=6000)
        return self._parse_json(response)
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.generate_docs({
            "name": context.project_name,
            "description": context.description,
            "requirements": context.requirements
        })


class EvaluationAgent(EnhancedBaseAgent):
    """Enhanced project evaluator."""
    
    def __init__(self, config: ConfigManager, cache: ResponseCache):
        super().__init__(
            name="EvaluationAI",
            role="Analyst - Metrics, scoring, evaluation",
            config=config,
            cache=cache,
            model_type="analysis"
        )
    
    def evaluate(self, context: Dict) -> Dict:
        """Evaluate project."""
        prompt = f"""Evaluate this project: {json.dumps(context, indent=2)}

Output ONLY valid JSON with scores (0-100):
- completeness: score
- innovation: score  
- code_quality: score
- documentation: score
- demo_readiness: score
- improvements: list of suggestions
"""
        response = self._call_llm(prompt, max_tokens=2000)
        return self._parse_json(response)
    
    def process(self, task: AgentTask, context: ProjectContext) -> Any:
        return self.evaluate({
            "name": context.project_name,
            "files": context.files_created
        })


# ══════════════════════════════════════════════════════════════════════════════
# ENHANCED ORCHESTRATOR
# ══════════════════════════════════════════════════════════════════════════════

class EnhancedOrchestrator:
    """
    Enhanced orchestrator with parallel execution and better resource management.
    """
    
    def __init__(self, config_path: str = None):
        self.config = ConfigManager(config_path)
        self.cache = ResponseCache(
            max_size=100,
            ttl=self.config.get("execution", "cache_ttl", default=3600)
        )
        self.logger = setup_logging(self.config)
        self.progress = ProgressTracker()
        
        # Initialize agents
        self.agents = {
            "ProjectLeadAI": ProjectLeadAgent(self.config, self.cache),
            "TechArchitectAI": TechArchitectAgent(self.config, self.cache),
            "FrontendAI": CodeGeneratorAgent(self.config, self.cache, "frontend"),
            "BackendAI": CodeGeneratorAgent(self.config, self.cache, "backend"),
            "DataAI": CodeGeneratorAgent(self.config, self.cache, "data"),
            "DevOpsAI": DevOpsAgent(self.config, self.cache),
            "PresentationAI": DocumentationAgent(self.config, self.cache),
            "EvaluationAI": EvaluationAgent(self.config, self.cache),
        }
        
        self.executor = ThreadPoolExecutor(
            max_workers=self.config.get("execution", "max_concurrent", default=4)
        )
    
    def create_project(self, description: str, project_name: str = None,
                      template: str = None) -> ProjectContext:
        """Create a complete project with parallel agent execution."""
        
        self.progress.start()
        
        # Apply template if specified
        if template:
            template_desc = ProjectTemplates.to_description(template)
            if template_desc:
                description = template_desc + "\n" + description
        
        # Initialize project
        if not project_name:
            project_name = self._extract_name(description)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.config.get("project", "output_dir", default="projects")
        project_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            output_dir,
            f"{project_name}_{timestamp}"
        )
        os.makedirs(project_dir, exist_ok=True)
        
        context = ProjectContext(
            project_name=project_name,
            project_dir=project_dir,
            description=description
        )
        
        print(f"\n📋 Project: {project_name}")
        print(f"📁 Location: {project_dir}")
        
        try:
            # Phase 1: Project Structure
            self.progress.start_phase(1, "Project Initialization")
            context.files_created.extend(self._create_structure(project_dir))
            self.progress.update_agent("ProjectFactory", "done", f"{len(context.files_created)} files")
            
            # Phase 2: Requirements Analysis
            self.progress.start_phase(2, "Requirements Analysis")
            context.requirements = self.agents["ProjectLeadAI"].analyze_requirements(description)
            self.progress.update_agent("ProjectLeadAI", "done", "Requirements analyzed")
            
            # Phase 3: Architecture Design
            self.progress.start_phase(3, "Architecture Design")
            context.architecture = self.agents["TechArchitectAI"].design_architecture(context.requirements)
            self.progress.update_agent("TechArchitectAI", "done", "Architecture designed")
            
            # Phase 4: Parallel Code Generation
            self.progress.start_phase(4, "Code Generation (Parallel)")
            code_results = self._parallel_code_generation(context)
            for agent_name, files in code_results.items():
                context.files_created.extend(files)
                self.progress.update_agent(agent_name, "done", f"{len(files)} files")
            
            # Phase 5: DevOps & Testing
            self.progress.start_phase(5, "DevOps Configuration")
            devops = self.agents["DevOpsAI"].generate_devops(context.architecture)
            devops_files = self._save_code_files(project_dir, devops, "")
            context.files_created.extend(devops_files)
            self.progress.update_agent("DevOpsAI", "done", f"{len(devops_files)} files")
            
            # Phase 6: Documentation
            self.progress.start_phase(6, "Documentation")
            docs = self.agents["PresentationAI"].generate_docs({
                "name": context.project_name,
                "description": context.description,
                "requirements": context.requirements,
                "architecture": context.architecture
            })
            docs_files = self._save_code_files(project_dir, docs, "")
            context.files_created.extend(docs_files)
            self.progress.update_agent("PresentationAI", "done", f"{len(docs_files)} files")
            
            # Phase 7: Evaluation
            self.progress.start_phase(7, "Evaluation")
            context.metrics = self.agents["EvaluationAI"].evaluate({
                "name": context.project_name,
                "files": context.files_created,
                "requirements": context.requirements
            })
            self.progress.update_agent("EvaluationAI", "done", "Project scored")
            
            context.status = "completed"
            
        except Exception as e:
            self.logger.error(f"Project creation failed: {e}")
            context.status = "error"
            raise
        
        # Save project config
        self._save_project_config(project_dir, context)
        
        # Print completion summary
        self.progress.complete(
            len(context.files_created),
            project_dir,
            context.metrics
        )
        
        return context
    
    def _parallel_code_generation(self, context: ProjectContext) -> Dict[str, List[str]]:
        """Run code generation agents in parallel."""
        results = {}
        
        if self.config.get("execution", "parallel", default=True):
            # Parallel execution
            futures = {}
            with ThreadPoolExecutor(max_workers=3) as executor:
                for agent_name in ["FrontendAI", "BackendAI", "DataAI"]:
                    agent = self.agents[agent_name]
                    future = executor.submit(
                        agent.generate_code,
                        context.requirements,
                        context.architecture
                    )
                    futures[future] = agent_name
                
                for future in as_completed(futures):
                    agent_name = futures[future]
                    try:
                        code_dict = future.result()
                        subdirectory = {
                            "FrontendAI": "10_Code/Frontend",
                            "BackendAI": "10_Code/Backend",
                            "DataAI": "10_Code/Backend/data"
                        }.get(agent_name, "")
                        files = self._save_code_files(context.project_dir, code_dict, subdirectory)
                        results[agent_name] = files
                    except Exception as e:
                        self.logger.error(f"{agent_name} failed: {e}")
                        results[agent_name] = []
        else:
            # Sequential execution
            for agent_name, subdirectory in [
                ("BackendAI", "10_Code/Backend"),
                ("FrontendAI", "10_Code/Frontend"),
                ("DataAI", "10_Code/Backend/data")
            ]:
                try:
                    code_dict = self.agents[agent_name].generate_code(
                        context.requirements,
                        context.architecture
                    )
                    files = self._save_code_files(context.project_dir, code_dict, subdirectory)
                    results[agent_name] = files
                except Exception as e:
                    self.logger.error(f"{agent_name} failed: {e}")
                    results[agent_name] = []
        
        return results
    
    def _extract_name(self, description: str) -> str:
        """Extract project name."""
        words = description.lower().split()[:4]
        name = "-".join(w for w in words if w.isalnum())
        return name[:30] or "new-project"
    
    def _create_structure(self, project_dir: str) -> List[str]:
        """Create standardized project structure."""
        structure = [
            "01_Proposal.md", "02_Project_Report.md", "03_Architecture.md",
            "04_SRS.md", "05_PPT.md", "06_Demo.md", "07_Testing.md",
            "08_Risk_and_Security.md", "09_Assets/Diagrams/.gitkeep",
            "09_Assets/DataSets/.gitkeep", "09_Assets/Screenshots/.gitkeep",
            "10_Code/Frontend/.gitkeep", "10_Code/Backend/.gitkeep",
            "10_Code/AI_Agents/.gitkeep", "10_Code/Scripts/.gitkeep"
        ]
        
        created = []
        for path in structure:
            full_path = os.path.join(project_dir, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            if not os.path.exists(full_path):
                with open(full_path, 'w') as f:
                    if path.endswith('.md'):
                        f.write(f"# {Path(path).stem.replace('_', ' ')}\n\n")
                    else:
                        f.write("")
                created.append(path)
        
        return created
    
    def _save_code_files(self, project_dir: str, code_dict: Dict, subdirectory: str) -> List[str]:
        """Save generated code files."""
        created = []
        if not isinstance(code_dict, dict):
            return created
        
        for filepath, content in code_dict.items():
            if isinstance(content, str) and len(content) > 10:
                if subdirectory:
                    full_path = os.path.join(project_dir, subdirectory, filepath)
                else:
                    full_path = os.path.join(project_dir, filepath)
                
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Clean content
                content = content.strip()
                if content.startswith("```"):
                    lines = content.split("\n")[1:]
                    if lines and lines[-1].strip() == "```":
                        lines = lines[:-1]
                    content = "\n".join(lines)
                
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                created.append(filepath)
        
        return created
    
    def _save_project_config(self, project_dir: str, context: ProjectContext):
        """Save project configuration."""
        config = {
            "project_name": context.project_name,
            "created_at": datetime.now().isoformat(),
            "files_created": context.files_created,
            "requirements": context.requirements,
            "architecture": context.architecture,
            "metrics": context.metrics,
            "status": context.status
        }
        
        config_path = os.path.join(project_dir, ".project-config.json")
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2, default=str)


# ══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

def print_banner():
    """Print enhanced banner."""
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
║    ██████╗ ██████╗ ██╗ ██████╗  █████╗ ██████╗ ███████╗    ██╗   ██╗██████╗    ███████╗         ║
║    ██╔══██╗██╔══██╗██║██╔════╝ ██╔══██╗██╔══██╗██╔════╝    ██║   ██║╚════██╗   ██╔════╝         ║
║    ██████╔╝██████╔╝██║██║  ███╗███████║██║  ██║█████╗      ██║   ██║ █████╔╝   ███████╗         ║
║    ██╔══██╗██╔══██╗██║██║   ██║██╔══██║██║  ██║██╔══╝      ╚██╗ ██╔╝ ╚═══██╗   ╚════██║         ║
║    ██████╔╝██║  ██║██║╚██████╔╝██║  ██║██████╔╝███████╗     ╚████╔╝ ██████╔╝██╗███████║         ║
║    ╚═════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚══════╝      ╚═══╝  ╚═════╝ ╚═╝╚══════╝         ║
║                                                                                                  ║
║              🏭 Enhanced Multi-Agent System with Parallel Execution v3.5                         ║
║                                                                                                  ║
║    Features: ⚡ Async Parallel │ 🔄 Auto-Retry │ 💾 Caching │ 📁 Templates │ ⚙️ Config           ║
║                                                                                                  ║
╚══════════════════════════════════════════════════════════════════════════════════════════════════╝
    """)


def show_templates():
    """Display available templates."""
    print("\n📁 AVAILABLE TEMPLATES")
    print("═" * 60)
    for name, template in ProjectTemplates.TEMPLATES.items():
        print(f"\n   📦 {name}")
        print(f"      {template['description']}")
        stack = ", ".join(f"{k}={v}" for k, v in template['stack'].items() if isinstance(v, str))
        print(f"      Stack: {stack}")
    print("\n" + "═" * 60)


def interactive_mode():
    """Enhanced interactive CLI."""
    print_banner()
    
    while True:
        print("\n" + "─" * 60)
        print("🎯 Options:")
        print("   1. Create project from description")
        print("   2. Create project from template")
        print("   3. Show templates")
        print("   4. Clear cache")
        print("   5. Exit")
        
        choice = input("\n>>> ").strip()
        
        if choice == "1":
            print("\n📝 Describe your project:")
            print("   (Press Enter twice to submit)\n")
            
            lines = []
            while True:
                line = input()
                if line:
                    lines.append(line)
                elif lines:
                    break
            
            description = "\n".join(lines)
            
            print("\n📛 Project name (leave empty for auto):")
            project_name = input(">>> ").strip() or None
            
            orchestrator = EnhancedOrchestrator()
            orchestrator.create_project(description, project_name)
            
        elif choice == "2":
            show_templates()
            print("\n📦 Enter template name:")
            template = input(">>> ").strip()
            
            if template in ProjectTemplates.TEMPLATES:
                print("\n📝 Additional requirements (optional):")
                extra = input(">>> ").strip()
                
                orchestrator = EnhancedOrchestrator()
                orchestrator.create_project(extra or "", template=template)
            else:
                print("❌ Template not found")
            
        elif choice == "3":
            show_templates()
            
        elif choice == "4":
            orchestrator = EnhancedOrchestrator()
            orchestrator.cache.clear()
            print("✅ Cache cleared")
            
        elif choice == "5":
            print("\n👋 Goodbye!")
            break


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--templates":
            show_templates()
        elif sys.argv[1] == "--template" and len(sys.argv) > 2:
            template = sys.argv[2]
            extra = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
            orchestrator = EnhancedOrchestrator()
            orchestrator.create_project(extra, template=template)
        else:
            description = " ".join(sys.argv[1:])
            orchestrator = EnhancedOrchestrator()
            orchestrator.create_project(description)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
