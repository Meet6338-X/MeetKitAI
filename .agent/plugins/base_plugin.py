"""
KARYA AGENT - Plugin Base Class
═══════════════════════════════════════════════════════════════════════════════

Base class for all plugin agents. Extend this to create custom agents.

Usage:
    from plugins import register_agent
    from plugins.base_plugin import PluginBase
    
    @register_agent("MyCustomAI")
    class MyCustomAgent(PluginBase):
        def __init__(self):
            super().__init__(
                name="MyCustomAI",
                role="Custom Role Description",
                capabilities=["custom_feature"]
            )
        
        def process(self, task, context):
            # Your processing logic
            return {"result": "processed"}

Version: 1.0.0
"""

import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class PluginMetadata:
    """Plugin metadata information."""
    name: str
    version: str = "1.0.0"
    author: str = "KARYA AGENT"
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    enabled: bool = True


class PluginBase(ABC):
    """
    Base class for all plugin agents.
    
    All custom agents should extend this class and implement the process method.
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        capabilities: List[str] = None,
        model_type: str = "reasoning",
        metadata: PluginMetadata = None
    ):
        self.name = name
        self.role = role
        self.capabilities = capabilities or []
        self.model_type = model_type
        self.metadata = metadata or PluginMetadata(name=name)
        
        # Runtime state
        self.status = "idle"
        self.tasks_completed = 0
        self.last_run = None
        self.errors = []
        
        # Configuration
        self.config: Dict[str, Any] = {}
        
        logger.info(f"Plugin initialized: {name}")
    
    @abstractmethod
    def process(self, task: Any, context: Any) -> Any:
        """
        Process a task. Must be implemented by subclasses.
        
        Args:
            task: The task to process
            context: Project context with shared state
        
        Returns:
            Processing result (dict, str, or any serializable type)
        """
        pass
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the plugin with custom settings."""
        self.config.update(config)
    
    def validate(self) -> bool:
        """Validate plugin configuration. Override for custom validation."""
        return True
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for LLM calls.
        Override to customize the agent's behavior.
        """
        return f"""You are {self.name}, a specialized AI agent.
Role: {self.role}

Capabilities:
{chr(10).join(f'- {cap}' for cap in self.capabilities)}

Provide detailed, actionable output for your assigned tasks.
Format your responses in clean, structured markdown when appropriate.
"""
    
    def pre_process(self, task: Any, context: Any) -> None:
        """Hook called before processing. Override for setup logic."""
        self.status = "working"
        self.last_run = datetime.now()
    
    def post_process(self, task: Any, context: Any, result: Any) -> Any:
        """Hook called after processing. Override for cleanup or result modification."""
        self.status = "completed"
        self.tasks_completed += 1
        return result
    
    def on_error(self, task: Any, context: Any, error: Exception) -> None:
        """Hook called on error. Override for custom error handling."""
        self.status = "error"
        self.errors.append({
            "time": datetime.now().isoformat(),
            "task": str(task),
            "error": str(error)
        })
        logger.error(f"Plugin {self.name} error: {error}")
    
    def run(self, task: Any, context: Any) -> Any:
        """
        Execute the plugin with pre/post hooks and error handling.
        This is the main entry point for running the plugin.
        """
        try:
            self.pre_process(task, context)
            result = self.process(task, context)
            return self.post_process(task, context, result)
        except Exception as e:
            self.on_error(task, context, e)
            raise
    
    def get_status(self) -> Dict[str, Any]:
        """Get plugin status information."""
        return {
            "name": self.name,
            "status": self.status,
            "tasks_completed": self.tasks_completed,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "error_count": len(self.errors)
        }
    
    def __repr__(self) -> str:
        return f"<Plugin: {self.name} ({self.status})>"


class LLMPluginBase(PluginBase):
    """
    Base class for plugins that use LLM for processing.
    Provides built-in LLM calling capabilities.
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        capabilities: List[str] = None,
        model_type: str = "reasoning",
        api_key: str = None,
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = None
    ):
        super().__init__(name, role, capabilities, model_type)
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY", "")
        self.base_url = base_url
        self.model = model or "google/gemini-2.0-flash-001"
        
        self._client = None
    
    @property
    def client(self):
        """Lazy load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                logger.error("OpenAI package not installed")
                raise
        return self._client
    
    def call_llm(self, prompt: str, max_tokens: int = 4000, temperature: float = 0.7) -> str:
        """
        Make an LLM API call.
        
        Args:
            prompt: The user prompt
            max_tokens: Maximum response tokens
            temperature: Creativity level (0-1)
        
        Returns:
            LLM response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise


class ToolPluginBase(PluginBase):
    """
    Base class for plugins that provide tools/functions.
    Use this for utility plugins that don't use LLM.
    """
    
    def __init__(self, name: str, role: str, capabilities: List[str] = None):
        super().__init__(name, role, capabilities, model_type="tool")
        self.tools: Dict[str, callable] = {}
    
    def register_tool(self, name: str, func: callable, description: str = "") -> None:
        """Register a tool function."""
        self.tools[name] = {
            "function": func,
            "description": description
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get all registered tools."""
        return [
            {"name": name, "description": tool["description"]}
            for name, tool in self.tools.items()
        ]
    
    def call_tool(self, name: str, *args, **kwargs) -> Any:
        """Call a registered tool."""
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        return self.tools[name]["function"](*args, **kwargs)
