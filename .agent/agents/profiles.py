"""
KARYA AGENT - Project Profiles System
═══════════════════════════════════════════════════════════════════════════════

Domain-specific project configurations for rapid project generation.
Each profile pre-configures: agents, folder structure, tech stack, and validation.

Usage:
    from profiles import get_profile, list_profiles, ProfileManager
    
    profile = get_profile("web_app")
    print(profile.agents)
    print(profile.structure)

Version: 1.0.0
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class ProjectType(Enum):
    """Available project types."""
    WEB_APP = "web_app"
    ML_PROJECT = "ml_project"
    MOBILE_APP = "mobile_app"
    CLI_TOOL = "cli_tool"
    MICROSERVICES = "microservices"
    API_BACKEND = "api_backend"
    DATA_PIPELINE = "data_pipeline"
    IOT_PROJECT = "iot_project"
    DESKTOP_APP = "desktop_app"
    GAME = "game"


@dataclass
class TechStack:
    """Technology stack configuration."""
    frontend: Optional[str] = None
    backend: Optional[str] = None
    database: Optional[str] = None
    cache: Optional[str] = None
    queue: Optional[str] = None
    ml_framework: Optional[str] = None
    containerization: str = "docker"
    ci_cd: str = "github-actions"
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class ProjectProfile:
    """Complete project profile configuration."""
    name: str
    description: str
    project_type: ProjectType
    agents: List[str]
    structure: List[str]
    tech_stack: TechStack
    doc_templates: List[str]
    validation_rules: List[str] = field(default_factory=list)
    recommended_for: List[str] = field(default_factory=list)
    estimated_complexity: str = "medium"  # low, medium, high, enterprise
    
    def get_enabled_agents(self) -> Dict[str, bool]:
        """Return agent enable/disable config."""
        all_agents = [
            "ProjectLeadAI", "TechArchitectAI", "DataEngineerAI",
            "FrontendAI", "BackendAI", "FeatureAI", "PresentationAI",
            "IntegrationAI", "EvaluationAI", "DevOpsAI", "SecurityAI",
            "FeedbackLoopAI"
        ]
        return {agent: agent in self.agents for agent in all_agents}


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE DEFINITIONS
# ══════════════════════════════════════════════════════════════════════════════

PROFILES: Dict[str, ProjectProfile] = {
    
    # ──────────────────────────────────────────────────────────────────────────
    # WEB APPLICATION
    # ──────────────────────────────────────────────────────────────────────────
    "web_app": ProjectProfile(
        name="Full-Stack Web Application",
        description="Complete web application with frontend, backend, and database",
        project_type=ProjectType.WEB_APP,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "FrontendAI", "BackendAI",
            "DevOpsAI", "SecurityAI", "IntegrationAI", "EvaluationAI"
        ],
        structure=[
            "10_Code/Frontend/src/",
            "10_Code/Frontend/public/",
            "10_Code/Frontend/package.json",
            "10_Code/Backend/app/",
            "10_Code/Backend/tests/",
            "10_Code/Backend/requirements.txt",
            "10_Code/Database/migrations/",
            "10_Code/Database/seeds/",
            "docker-compose.yml",
            "Dockerfile.frontend",
            "Dockerfile.backend",
            ".github/workflows/ci.yml",
        ],
        tech_stack=TechStack(
            frontend="react",
            backend="fastapi",
            database="postgresql",
            cache="redis",
            containerization="docker",
            ci_cd="github-actions"
        ),
        doc_templates=[
            "01_Proposal.md", "02_Project_Report.md", "03_Architecture.md",
            "04_SRS.md", "05_PPT.md", "06_Demo.md", "07_Testing.md",
            "08_Risk_and_Security.md", "11_Deployment.md"
        ],
        validation_rules=["has_frontend", "has_backend", "has_dockerfile", "has_tests"],
        recommended_for=["SaaS", "Dashboard", "E-commerce", "Portal", "Admin Panel"],
        estimated_complexity="high"
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # ML/AI PROJECT
    # ──────────────────────────────────────────────────────────────────────────
    "ml_project": ProjectProfile(
        name="Machine Learning Project",
        description="ML pipeline with data processing, training, and inference API",
        project_type=ProjectType.ML_PROJECT,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "DataEngineerAI", "FeatureAI",
            "BackendAI", "DevOpsAI", "EvaluationAI", "IntegrationAI"
        ],
        structure=[
            "10_Code/Data/raw/",
            "10_Code/Data/processed/",
            "10_Code/Data/features/",
            "10_Code/Models/training/",
            "10_Code/Models/inference/",
            "10_Code/Models/saved/",
            "10_Code/Notebooks/exploration/",
            "10_Code/Notebooks/experiments/",
            "10_Code/API/",
            "10_Code/Scripts/preprocess.py",
            "10_Code/Scripts/train.py",
            "10_Code/Scripts/evaluate.py",
            "config/model_config.yaml",
            "requirements.txt",
            "Dockerfile",
        ],
        tech_stack=TechStack(
            backend="fastapi",
            database="postgresql",
            ml_framework="pytorch",
            containerization="docker"
        ),
        doc_templates=[
            "01_Proposal.md", "02_Project_Report.md", "03_Architecture.md",
            "04_SRS.md", "06_Demo.md", "07_Testing.md",
            "ML_Model_Card.md", "Data_Dictionary.md"
        ],
        validation_rules=["has_data_dir", "has_model", "has_training_script"],
        recommended_for=["Prediction", "Classification", "NLP", "Computer Vision", "Recommendation"],
        estimated_complexity="high"
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # MOBILE APPLICATION
    # ──────────────────────────────────────────────────────────────────────────
    "mobile_app": ProjectProfile(
        name="Mobile Application",
        description="Cross-platform mobile app with React Native or Flutter",
        project_type=ProjectType.MOBILE_APP,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "FrontendAI", "BackendAI",
            "SecurityAI", "IntegrationAI", "DevOpsAI", "EvaluationAI"
        ],
        structure=[
            "10_Code/Mobile/src/screens/",
            "10_Code/Mobile/src/components/",
            "10_Code/Mobile/src/navigation/",
            "10_Code/Mobile/src/services/",
            "10_Code/Mobile/src/store/",
            "10_Code/Mobile/assets/",
            "10_Code/Backend/",
            "10_Code/Backend/api/",
            ".github/workflows/mobile-ci.yml",
        ],
        tech_stack=TechStack(
            frontend="react-native",
            backend="fastapi",
            database="postgresql",
            cache="redis"
        ),
        doc_templates=[
            "01_Proposal.md", "02_Project_Report.md", "03_Architecture.md",
            "04_SRS.md", "06_Demo.md", "07_Testing.md", "App_Store_Submission.md"
        ],
        validation_rules=["has_mobile_screens", "has_backend_api"],
        recommended_for=["Consumer Apps", "Enterprise Mobile", "Social Apps", "Utility Apps"],
        estimated_complexity="high"
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # CLI TOOL
    # ──────────────────────────────────────────────────────────────────────────
    "cli_tool": ProjectProfile(
        name="Command-Line Tool",
        description="CLI application with rich interface and configuration",
        project_type=ProjectType.CLI_TOOL,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "BackendAI",
            "IntegrationAI", "DevOpsAI", "EvaluationAI"
        ],
        structure=[
            "10_Code/src/cli/",
            "10_Code/src/commands/",
            "10_Code/src/utils/",
            "10_Code/src/config/",
            "10_Code/tests/",
            "setup.py",
            "pyproject.toml",
            "requirements.txt",
        ],
        tech_stack=TechStack(
            backend="python",
            containerization="docker"
        ),
        doc_templates=[
            "01_Proposal.md", "02_Project_Report.md", "03_Architecture.md",
            "06_Demo.md", "07_Testing.md", "CLI_Usage.md"
        ],
        validation_rules=["has_cli_entry", "has_pyproject", "has_tests"],
        recommended_for=["DevTools", "Automation", "System Utils", "Data Processing"],
        estimated_complexity="medium"
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # MICROSERVICES
    # ──────────────────────────────────────────────────────────────────────────
    "microservices": ProjectProfile(
        name="Microservices Architecture",
        description="Distributed system with multiple services and API gateway",
        project_type=ProjectType.MICROSERVICES,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "BackendAI", "DataEngineerAI",
            "DevOpsAI", "SecurityAI", "IntegrationAI", "EvaluationAI"
        ],
        structure=[
            "10_Code/Services/gateway/",
            "10_Code/Services/auth-service/",
            "10_Code/Services/user-service/",
            "10_Code/Services/notification-service/",
            "10_Code/Shared/common/",
            "10_Code/Shared/proto/",
            "docker-compose.yml",
            "docker-compose.dev.yml",
            "kubernetes/",
            ".github/workflows/",
        ],
        tech_stack=TechStack(
            backend="fastapi",
            database="postgresql",
            cache="redis",
            queue="rabbitmq",
            containerization="docker"
        ),
        doc_templates=[
            "01_Proposal.md", "02_Project_Report.md", "03_Architecture.md",
            "04_SRS.md", "06_Demo.md", "07_Testing.md", "08_Risk_and_Security.md",
            "Service_Contracts.md", "API_Gateway_Spec.md"
        ],
        validation_rules=["has_multiple_services", "has_gateway", "has_docker_compose"],
        recommended_for=["Enterprise", "High-Scale", "Distributed Systems"],
        estimated_complexity="enterprise"
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # API BACKEND
    # ──────────────────────────────────────────────────────────────────────────
    "api_backend": ProjectProfile(
        name="REST API Backend",
        description="Standalone API backend with authentication and database",
        project_type=ProjectType.API_BACKEND,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "BackendAI",
            "SecurityAI", "DevOpsAI", "IntegrationAI", "EvaluationAI"
        ],
        structure=[
            "10_Code/app/api/",
            "10_Code/app/models/",
            "10_Code/app/services/",
            "10_Code/app/schemas/",
            "10_Code/app/core/",
            "10_Code/tests/",
            "10_Code/migrations/",
            "requirements.txt",
            "Dockerfile",
            "docker-compose.yml",
        ],
        tech_stack=TechStack(
            backend="fastapi",
            database="postgresql",
            cache="redis",
            containerization="docker"
        ),
        doc_templates=[
            "01_Proposal.md", "03_Architecture.md", "04_SRS.md",
            "06_Demo.md", "07_Testing.md", "API_Documentation.md"
        ],
        validation_rules=["has_api_routes", "has_models", "has_tests"],
        recommended_for=["API Services", "Backend-only", "Headless CMS"],
        estimated_complexity="medium"
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # DATA PIPELINE
    # ──────────────────────────────────────────────────────────────────────────
    "data_pipeline": ProjectProfile(
        name="Data Pipeline",
        description="ETL/ELT pipeline with data orchestration",
        project_type=ProjectType.DATA_PIPELINE,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "DataEngineerAI",
            "DevOpsAI", "IntegrationAI", "EvaluationAI"
        ],
        structure=[
            "10_Code/Pipelines/extract/",
            "10_Code/Pipelines/transform/",
            "10_Code/Pipelines/load/",
            "10_Code/Orchestration/dags/",
            "10_Code/Data/schemas/",
            "10_Code/Tests/",
            "config/",
            "docker-compose.yml",
        ],
        tech_stack=TechStack(
            backend="python",
            database="postgresql",
            containerization="docker"
        ),
        doc_templates=[
            "01_Proposal.md", "03_Architecture.md", "06_Demo.md",
            "Data_Dictionary.md", "Pipeline_Documentation.md"
        ],
        validation_rules=["has_pipeline_stages", "has_orchestration"],
        recommended_for=["Data Engineering", "ETL", "Analytics"],
        estimated_complexity="high"
    ),
    
    # ──────────────────────────────────────────────────────────────────────────
    # IOT PROJECT
    # ──────────────────────────────────────────────────────────────────────────
    "iot_project": ProjectProfile(
        name="IoT Project",
        description="IoT system with device management and data collection",
        project_type=ProjectType.IOT_PROJECT,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "BackendAI", "DataEngineerAI",
            "FrontendAI", "SecurityAI", "DevOpsAI", "EvaluationAI"
        ],
        structure=[
            "10_Code/Device/firmware/",
            "10_Code/Device/protocols/",
            "10_Code/Gateway/",
            "10_Code/Backend/",
            "10_Code/Dashboard/",
            "10_Code/Data/timeseries/",
            "docker-compose.yml",
        ],
        tech_stack=TechStack(
            frontend="react",
            backend="fastapi",
            database="timescaledb",
            queue="mqtt",
            containerization="docker"
        ),
        doc_templates=[
            "01_Proposal.md", "03_Architecture.md", "04_SRS.md",
            "06_Demo.md", "Device_Spec.md", "Protocol_Doc.md"
        ],
        validation_rules=["has_device_code", "has_backend", "has_dashboard"],
        recommended_for=["Smart Home", "Industrial IoT", "Monitoring Systems"],
        estimated_complexity="enterprise"
    ),
    # ──────────────────────────────────────────────────────────────────────────
    # CHROME EXTENSION
    # ──────────────────────────────────────────────────────────────────────────
    "chrome_extension": ProjectProfile(
        name="Chrome Extension",
        description="Browser extension with popup, background scripts, and content scripts",
        project_type=ProjectType.WEB_APP, # Treating as web app variant
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "FrontendAI", "BackendAI", # Backend for any api calls
            "SecurityAI", "IntegrationAI"
        ],
        structure=[
            "10_Code/src/manifest.json",
            "10_Code/src/background/",
            "10_Code/src/content/",
            "10_Code/src/popup/",
            "10_Code/src/options/",
            "10_Code/assets/icons/",
            "webpack.config.js",
            "package.json",
            "README.md",
        ],
        tech_stack=TechStack(
            frontend="react", # Common to use React/Vue for complex popups
            backend="node",    # Build scripts
            containerization="none"
        ),
        doc_templates=[
            "01_Proposal.md", "03_Architecture.md", "06_Demo.md",
            "Extension_Store_Listing.md"
        ],
        validation_rules=["has_manifest"],
        recommended_for=["Browser Tools", "Productivity", "Web Scrapers"],
        estimated_complexity="medium"
    ),

    # ──────────────────────────────────────────────────────────────────────────
    # DESKTOP APPLICATION (GUI)
    # ──────────────────────────────────────────────────────────────────────────
    "desktop_app": ProjectProfile(
        name="Desktop Application",
        description="Cross-platform desktop GUI application",
        project_type=ProjectType.DESKTOP_APP,
        agents=[
            "ProjectLeadAI", "TechArchitectAI", "FrontendAI", "BackendAI",
            "DevOpsAI", "IntegrationAI"
        ],
        structure=[
            "10_Code/src/main.py",
            "10_Code/src/ui/",
            "10_Code/src/core/",
            "10_Code/src/assets/",
            "10_Code/tests/",
            "requirements.txt",
            "build_installer.py",
            "README.md",
        ],
        tech_stack=TechStack(
            frontend="pyqt",
            backend="python",
            containerization="none"
        ),
        doc_templates=[
            "01_Proposal.md", "03_Architecture.md", "06_Demo.md", "User_Manual.md"
        ],
        validation_rules=["has_gui_main"],
        recommended_for=["Internal Tools", "Media Editors", "System Utilities"],
        estimated_complexity="medium"
    ),
}


# ══════════════════════════════════════════════════════════════════════════════
# PROFILE MANAGER
# ══════════════════════════════════════════════════════════════════════════════

class ProfileManager:
    """Manages project profiles and provides utilities."""
    
    def __init__(self):
        self.profiles = PROFILES
    
    def get_profile(self, name: str) -> Optional[ProjectProfile]:
        """Get a profile by name."""
        return self.profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """List all available profile names."""
        return list(self.profiles.keys())
    
    def get_profile_info(self, name: str) -> Dict[str, Any]:
        """Get detailed profile information."""
        profile = self.profiles.get(name)
        if not profile:
            return {}
        return {
            "name": profile.name,
            "description": profile.description,
            "type": profile.project_type.value,
            "agents": profile.agents,
            "complexity": profile.estimated_complexity,
            "recommended_for": profile.recommended_for
        }
    
    def suggest_profile(self, description: str) -> str:
        """Suggest a profile based on project description."""
        description = description.lower()
        
        # Keyword matching for profile suggestion
        keyword_map = {
            "ml_project": ["machine learning", "ml", "ai model", "training", "prediction", "neural", "deep learning"],
            "web_app": ["website", "web app", "dashboard", "portal", "saas", "frontend", "react", "vue"],
            "mobile_app": ["mobile", "ios", "android", "react native", "flutter", "app store"],
            "cli_tool": ["cli", "command line", "terminal", "script", "automation tool"],
            "microservices": ["microservice", "distributed", "kubernetes", "k8s", "multiple services"],
            "api_backend": ["api", "rest", "backend only", "server", "endpoint"],
            "data_pipeline": ["etl", "pipeline", "data processing", "airflow", "orchestration"],
            "iot_project": ["iot", "sensor", "device", "embedded", "mqtt", "hardware"],
            "chrome_extension": ["chrome extension", "firefox addon", "browser plugin", "manifest.json"],
            "desktop_app": ["desktop", "gui", "windows app", "mac app", "tkinter", "qt", "pyqt", "electron"],
        }
        
        scores = {profile: 0 for profile in keyword_map}
        for profile, keywords in keyword_map.items():
            for keyword in keywords:
                if keyword in description:
                    scores[profile] += 1
        
        best_match = max(scores, key=scores.get)
        return best_match if scores[best_match] > 0 else "web_app"
    
    def display_profiles(self) -> str:
        """Generate a formatted display of all profiles."""
        output = []
        output.append("\n🎯 AVAILABLE PROJECT PROFILES")
        output.append("=" * 60)
        
        for name, profile in self.profiles.items():
            output.append(f"\n📦 {name}")
            output.append(f"   {profile.name}")
            output.append(f"   {profile.description}")
            output.append(f"   Complexity: {profile.estimated_complexity}")
            output.append(f"   Agents: {len(profile.agents)}")
            if profile.recommended_for:
                output.append(f"   Best for: {', '.join(profile.recommended_for[:3])}")
        
        output.append("\n" + "=" * 60)
        return "\n".join(output)


# ══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

_manager = ProfileManager()

def get_profile(name: str) -> Optional[ProjectProfile]:
    """Get a project profile by name."""
    return _manager.get_profile(name)

def list_profiles() -> List[str]:
    """List all available profiles."""
    return _manager.list_profiles()

def suggest_profile(description: str) -> str:
    """Suggest best profile for a project description."""
    return _manager.suggest_profile(description)

def display_profiles() -> str:
    """Display all profiles in formatted output."""
    return _manager.display_profiles()


# ══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            print(display_profiles())
        elif sys.argv[1] == "--suggest" and len(sys.argv) > 2:
            desc = " ".join(sys.argv[2:])
            suggested = suggest_profile(desc)
            print(f"\n🎯 Suggested Profile: {suggested}")
            profile = get_profile(suggested)
            if profile:
                print(f"   {profile.name}")
                print(f"   {profile.description}")
        elif sys.argv[1] == "--info" and len(sys.argv) > 2:
            profile = get_profile(sys.argv[2])
            if profile:
                print(f"\n📦 {profile.name}")
                print(f"   {profile.description}")
                print(f"\n   Agents: {', '.join(profile.agents)}")
                print(f"\n   Structure:")
                for item in profile.structure[:5]:
                    print(f"      - {item}")
                if len(profile.structure) > 5:
                    print(f"      ... and {len(profile.structure) - 5} more")
            else:
                print(f"Profile '{sys.argv[2]}' not found.")
        else:
            print("Usage:")
            print("  python profiles.py --list              # List all profiles")
            print("  python profiles.py --suggest <desc>    # Suggest profile")
            print("  python profiles.py --info <name>       # Profile details")
    else:
        print(display_profiles())
