"""
╔════════════════════════════════════════════════════════════════════════════════╗
║                          NVIDIA NANO AGENT                                     ║
║              Local Inference Agent for Edge Computing                          ║
╚════════════════════════════════════════════════════════════════════════════════╝

This agent is designed for local inference on NVIDIA Jetson Nano or 
GPU-enabled systems. It provides fast, offline AI capabilities for:
- Code analysis and suggestions
- Quick project validation
- Local documentation generation

Author: KARYA AGENT System
Version: 1.0.0
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List

# Optional: For local inference with NVIDIA TensorRT or Ollama
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

# Ollama endpoint for local LLM inference
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "codellama:7b"  # Lightweight code model

# For cloud fallback
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")


# ══════════════════════════════════════════════════════════════════════════════
# LOCAL INFERENCE ENGINE
# ══════════════════════════════════════════════════════════════════════════════

class LocalInferenceEngine:
    """
    Handles local model inference via Ollama or direct API calls.
    Designed for edge devices like NVIDIA Jetson Nano.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL, use_local: bool = True):
        """
        Initialize the inference engine.
        
        Args:
            model: Model name to use (Ollama format or OpenRouter format)
            use_local: If True, attempt local inference first
        """
        self.model = model
        self.use_local = use_local
        self.is_local_available = self._check_local_availability()
        
    def _check_local_availability(self) -> bool:
        """Check if local Ollama server is running."""
        if not REQUESTS_AVAILABLE:
            return False
        try:
            response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate a response using the configured model.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated text response
        """
        if self.use_local and self.is_local_available:
            return self._generate_ollama(prompt, system_prompt)
        else:
            return self._generate_cloud(prompt, system_prompt)
    
    def _generate_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Generate using local Ollama server."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        if system_prompt:
            payload["system"] = system_prompt
            
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120
            )
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Error: {response.status_code}"
        except Exception as e:
            return f"Local inference error: {str(e)}"
    
    def _generate_cloud(self, prompt: str, system_prompt: str = None) -> str:
        """Fallback to cloud inference."""
        if not OPENROUTER_API_KEY:
            return "Error: No API key configured for cloud fallback"
        
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=OPENROUTER_API_KEY
            )
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = client.chat.completions.create(
                model="google/gemini-2.0-flash-001",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Cloud inference error: {str(e)}"


# ══════════════════════════════════════════════════════════════════════════════
# NVIDIA NANO AGENT
# ══════════════════════════════════════════════════════════════════════════════

class NvidiaNanoAgent:
    """
    Agent optimized for local inference on edge devices.
    Provides quick analysis and validation capabilities.
    """
    
    def __init__(self, use_local: bool = True):
        """Initialize the agent."""
        self.engine = LocalInferenceEngine(use_local=use_local)
        self.capabilities = [
            "code_analysis",
            "project_validation", 
            "quick_docs",
            "syntax_check",
            "dependency_analysis"
        ]
    
    def analyze_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code for issues, improvements, and best practices.
        
        Args:
            code: Source code to analyze
            language: Programming language
            
        Returns:
            Analysis results dictionary
        """
        prompt = f"""Analyze the following {language} code and provide:
1. Potential bugs or issues
2. Performance concerns
3. Best practice violations
4. Suggested improvements

Code:
```{language}
{code}
```

Provide concise, actionable feedback."""

        response = self.engine.generate(prompt)
        return {
            "language": language,
            "analysis": response,
            "timestamp": datetime.now().isoformat()
        }
    
    def validate_project_structure(self, structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a project structure for completeness.
        
        Args:
            structure: Dictionary representing folder structure
            
        Returns:
            Validation results
        """
        structure_str = json.dumps(structure, indent=2)
        prompt = f"""Review this project structure and identify:
1. Missing essential files (README, .gitignore, etc.)
2. Organizational issues
3. Missing test directories
4. Configuration gaps

Structure:
{structure_str}

Provide brief, specific recommendations."""

        response = self.engine.generate(prompt)
        return {
            "validation": response,
            "is_valid": "missing" not in response.lower(),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_quick_docs(self, code: str, doc_type: str = "docstring") -> str:
        """
        Generate quick documentation for code.
        
        Args:
            code: Source code
            doc_type: Type of docs (docstring, readme, api)
            
        Returns:
            Generated documentation
        """
        prompt = f"""Generate a {doc_type} for the following code:

```python
{code}
```

Be concise but comprehensive."""

        return self.engine.generate(prompt)
    
    def check_dependencies(self, requirements: List[str]) -> Dict[str, Any]:
        """
        Analyze project dependencies for issues.
        
        Args:
            requirements: List of dependencies (like requirements.txt lines)
            
        Returns:
            Dependency analysis results
        """
        deps_str = "\n".join(requirements)
        prompt = f"""Analyze these Python dependencies:

{deps_str}

Identify:
1. Version conflicts potential
2. Deprecated packages
3. Security concerns
4. Lighter alternatives if any

Be brief and practical."""

        response = self.engine.generate(prompt)
        return {
            "analysis": response,
            "dependency_count": len(requirements),
            "timestamp": datetime.now().isoformat()
        }


# ══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

def print_banner():
    """Print agent banner."""
    print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║   ███╗   ██╗██╗   ██╗██╗██████╗ ██╗ █████╗     ███╗   ██╗ █████╗ ███╗   ██╗   ║
║   ████╗  ██║██║   ██║██║██╔══██╗██║██╔══██╗    ████╗  ██║██╔══██╗████╗  ██║   ║
║   ██╔██╗ ██║██║   ██║██║██║  ██║██║███████║    ██╔██╗ ██║███████║██╔██╗ ██║   ║
║   ██║╚██╗██║╚██╗ ██╔╝██║██║  ██║██║██╔══██║    ██║╚██╗██║██╔══██║██║╚██╗██║   ║
║   ██║ ╚████║ ╚████╔╝ ██║██████╔╝██║██║  ██║    ██║ ╚████║██║  ██║██║ ╚████║   ║
║   ╚═╝  ╚═══╝  ╚═══╝  ╚═╝╚═════╝ ╚═╝╚═╝  ╚═╝    ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝   ║
║                                                                                ║
║                    ⚡ Edge Computing AI Agent                                   ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    """Main CLI entry point."""
    print_banner()
    
    agent = NvidiaNanoAgent()
    
    print(f"\n🔌 Local Inference: {'Available ✅' if agent.engine.is_local_available else 'Not Available (using cloud) ☁️'}")
    print(f"📋 Capabilities: {', '.join(agent.capabilities)}")
    print("\n" + "═" * 70)
    
    print("\n🎯 Select an option:")
    print("   1. Analyze Code")
    print("   2. Validate Project Structure")
    print("   3. Generate Quick Docs")
    print("   4. Check Dependencies")
    print("   5. Exit")
    
    while True:
        choice = input("\n>>> ").strip()
        
        if choice == "1":
            print("\nPaste your code (empty line to finish):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            code = "\n".join(lines)
            result = agent.analyze_code(code)
            print("\n📊 Analysis Result:")
            print(result["analysis"])
            
        elif choice == "2":
            print("\nEnter project structure as JSON:")
            structure = json.loads(input())
            result = agent.validate_project_structure(structure)
            print("\n✅ Validation Result:")
            print(result["validation"])
            
        elif choice == "3":
            print("\nPaste your code (empty line to finish):")
            lines = []
            while True:
                line = input()
                if not line:
                    break
                lines.append(line)
            code = "\n".join(lines)
            docs = agent.generate_quick_docs(code)
            print("\n📚 Generated Documentation:")
            print(docs)
            
        elif choice == "4":
            print("\nEnter dependencies (one per line, empty to finish):")
            deps = []
            while True:
                dep = input()
                if not dep:
                    break
                deps.append(dep)
            result = agent.check_dependencies(deps)
            print("\n📦 Dependency Analysis:")
            print(result["analysis"])
            
        elif choice == "5":
            print("\n👋 Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1-5.")


if __name__ == "__main__":
    main()