import os
import subprocess
import logging
from typing import List, Optional

logger = logging.getLogger("GitOps")

class GitOps:
    """
    Handles Git operations for generated projects.
    Enables 'Treat Generated Code as a Repo' philosophy.
    """
    
    @staticmethod
    def init_repo(project_dir: str) -> bool:
        """Initialize a new git repository."""
        try:
            # Check if git is installed
            subprocess.run(["git", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
            # Init repo
            subprocess.run(["git", "init"], cwd=project_dir, check=True, stdout=subprocess.DEVNULL)
            
            # Configure local user if not global (optional, skipping to avoid overwriting user config)
            # We assume the machine has git configured
            
            logger.info(f"Initialized git repo in {project_dir}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("Git not found or failed to initialize.")
            return False

    @staticmethod
    def create_gitignore(project_dir: str, tech_stack: List[str] = None):
        """Create a comprehensive .gitignore file."""
        # Base gitignore
        content = """
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
venv/
env/
ENV/
.env

# Editor configuration
.vscode/
.idea/
*.swp

# OS specific
.DS_Store
Thumbs.db

# Logs
*.log
logs/
"""
        # Tech stack specific additions
        if tech_stack:
            stack_str = " ".join(tech_stack).lower()
            if "node" in stack_str or "react" in stack_str or "vue" in stack_str:
                content += "\n# Node\nnode_modules/\nnpm-debug.log\nyarn-error.log\n.next/\nbuild/\ndist/\n"
            
            if "java" in stack_str:
                content += "\n# Java\n*.class\n*.jar\n*.war\ntarget/\n"
                
            if "docker" in stack_str:
                content += "\n# Docker\n.docker/\n"

        gitignore_path = os.path.join(project_dir, ".gitignore")
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, "w") as f:
                f.write(content)

    @staticmethod
    def commit(project_dir: str, message: str) -> bool:
        """Stage and commit all changes."""
        try:
             # Check if .git exists to avoid fatal errors
            if not os.path.exists(os.path.join(project_dir, ".git")):
                return False

            # Add all files
            subprocess.run(["git", "add", "."], cwd=project_dir, check=True, stdout=subprocess.DEVNULL)
            
            # Commit (allow empty if nothing changed to avoid error)
            subprocess.run(
                ["git", "commit", "-m", message, "--allow-empty"], 
                cwd=project_dir, 
                check=True, 
                stdout=subprocess.DEVNULL
            )
            logger.info(f"Git commit: {message}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Git commit failed: {e}")
            return False
