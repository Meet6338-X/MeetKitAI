"""
KARYA AGENT - Plugin System
═══════════════════════════════════════════════════════════════════════════════

Extensible plugin architecture for custom agents.

Usage:
    from plugins import register_agent, load_plugins, get_plugin
    
    @register_agent("CustomAI")
    class CustomAgent(PluginBase):
        def process(self, task, context):
            return "Custom processing"

Version: 1.0.0
"""

import os
import importlib
import importlib.util
from typing import Dict, Type, Any, Optional, List, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Plugin registry
_PLUGIN_REGISTRY: Dict[str, Type] = {}
_PLUGIN_INSTANCES: Dict[str, Any] = {}
_HOOKS: Dict[str, List[Callable]] = {}


def register_agent(name: str):
    """
    Decorator to register a custom agent plugin.
    
    Usage:
        @register_agent("CustomAI")
        class CustomAgent(PluginBase):
            ...
    """
    def decorator(cls):
        _PLUGIN_REGISTRY[name] = cls
        logger.info(f"Registered plugin: {name}")
        return cls
    return decorator


def register_hook(hook_name: str):
    """
    Decorator to register a hook function.
    
    Hooks: pre_generation, post_generation, pre_agent, post_agent
    
    Usage:
        @register_hook("post_generation")
        def my_hook(context):
            print("Running post-generation hook")
    """
    def decorator(func):
        if hook_name not in _HOOKS:
            _HOOKS[hook_name] = []
        _HOOKS[hook_name].append(func)
        logger.info(f"Registered hook: {hook_name} -> {func.__name__}")
        return func
    return decorator


def get_plugin(name: str) -> Optional[Type]:
    """Get a registered plugin class by name."""
    return _PLUGIN_REGISTRY.get(name)


def get_plugin_instance(name: str, *args, **kwargs) -> Optional[Any]:
    """Get or create a plugin instance."""
    if name not in _PLUGIN_INSTANCES:
        cls = get_plugin(name)
        if cls:
            _PLUGIN_INSTANCES[name] = cls(*args, **kwargs)
    return _PLUGIN_INSTANCES.get(name)


def list_plugins() -> List[str]:
    """List all registered plugins."""
    return list(_PLUGIN_REGISTRY.keys())


def run_hooks(hook_name: str, *args, **kwargs) -> List[Any]:
    """Run all registered hooks for a given hook point."""
    results = []
    for hook in _HOOKS.get(hook_name, []):
        try:
            result = hook(*args, **kwargs)
            results.append(result)
        except Exception as e:
            logger.error(f"Hook {hook.__name__} failed: {e}")
    return results


def load_plugins(plugins_dir: str = None) -> Dict[str, Type]:
    """
    Load all plugins from the plugins directory.
    
    Args:
        plugins_dir: Path to plugins directory. Defaults to ./plugins/
    
    Returns:
        Dictionary of loaded plugins
    """
    if plugins_dir is None:
        plugins_dir = Path(__file__).parent
    else:
        plugins_dir = Path(plugins_dir)
    
    if not plugins_dir.exists():
        logger.warning(f"Plugins directory not found: {plugins_dir}")
        return _PLUGIN_REGISTRY
    
    # Load all .py files in the plugins directory
    for plugin_file in plugins_dir.glob("*.py"):
        if plugin_file.name.startswith("_"):
            continue
        if plugin_file.name == "base_plugin.py":
            continue
            
        try:
            module_name = plugin_file.stem
            spec = importlib.util.spec_from_file_location(
                f"plugins.{module_name}",
                plugin_file
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                logger.info(f"Loaded plugin module: {module_name}")
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_file}: {e}")
    
    return _PLUGIN_REGISTRY


def get_all_agents() -> Dict[str, Type]:
    """Get all registered agent plugins."""
    return _PLUGIN_REGISTRY.copy()


# ══════════════════════════════════════════════════════════════════════════════
# PLUGIN DISCOVERY
# ══════════════════════════════════════════════════════════════════════════════

class PluginDiscovery:
    """Handles plugin discovery and loading."""
    
    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.loaded_modules = {}
    
    def discover(self) -> List[str]:
        """Discover available plugins."""
        plugins = []
        for f in self.base_dir.glob("*.py"):
            if not f.name.startswith("_") and f.name != "base_plugin.py":
                plugins.append(f.stem)
        return plugins
    
    def load_all(self) -> Dict[str, Type]:
        """Load all discovered plugins."""
        return load_plugins(str(self.base_dir))
    
    def reload(self, plugin_name: str) -> bool:
        """Reload a specific plugin."""
        plugin_file = self.base_dir / f"{plugin_name}.py"
        if not plugin_file.exists():
            return False
        
        try:
            spec = importlib.util.spec_from_file_location(
                f"plugins.{plugin_name}",
                plugin_file
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                self.loaded_modules[plugin_name] = module
                return True
        except Exception as e:
            logger.error(f"Failed to reload {plugin_name}: {e}")
        
        return False
