"""
KARYA AGENT - Example Plugin
═══════════════════════════════════════════════════════════════════════════════

Example custom agent plugin to demonstrate the plugin system.
Use this as a template for creating your own custom agents.

Version: 1.0.0
"""

from plugins import register_agent, register_hook
from plugins.base_plugin import LLMPluginBase, PluginMetadata
from typing import Any, Dict


# ══════════════════════════════════════════════════════════════════════════════
# EXAMPLE: Custom LLM Agent
# ══════════════════════════════════════════════════════════════════════════════

@register_agent("DocumentationAI")
class DocumentationAgent(LLMPluginBase):
    """
    Custom agent for generating advanced documentation.
    
    This demonstrates how to create a custom agent that:
    - Extends LLMPluginBase for LLM capabilities
    - Implements custom processing logic
    - Uses hooks for lifecycle management
    """
    
    def __init__(self):
        super().__init__(
            name="DocumentationAI",
            role="Technical Documentation Specialist - Creates comprehensive, developer-friendly documentation",
            capabilities=[
                "API documentation generation",
                "README creation",
                "Code comment generation",
                "User guide creation",
                "Changelog generation"
            ],
            model_type="creative",
            metadata=PluginMetadata(
                name="DocumentationAI",
                version="1.0.0",
                author="KARYA AGENT",
                description="Advanced documentation generation agent",
                tags=["documentation", "technical-writing"]
            )
        )
    
    def get_system_prompt(self) -> str:
        return """You are DocumentationAI, an expert technical writer and documentation specialist.

Your expertise includes:
- Creating clear, comprehensive API documentation
- Writing developer-friendly READMEs
- Generating helpful code comments
- Creating user guides and tutorials
- Writing changelogs and release notes

Guidelines:
1. Use clear, concise language
2. Include code examples where helpful
3. Structure content with proper headings
4. Add helpful diagrams in mermaid format when appropriate
5. Follow the specific project's style and conventions

Format your responses in clean, professional markdown."""
    
    def process(self, task: Any, context: Any) -> Dict[str, Any]:
        """
        Process a documentation task.
        
        Args:
            task: Task with 'doc_type' and 'content' fields
            context: Project context
        
        Returns:
            Generated documentation
        """
        doc_type = getattr(task, 'doc_type', 'readme')
        content = getattr(task, 'content', '')
        
        prompts = {
            "readme": f"Generate a comprehensive README.md for this project:\n\n{content}",
            "api": f"Generate API documentation for these endpoints:\n\n{content}",
            "changelog": f"Generate a changelog entry for these changes:\n\n{content}",
            "guide": f"Create a user guide for this feature:\n\n{content}",
        }
        
        prompt = prompts.get(doc_type, f"Generate documentation for:\n\n{content}")
        
        result = self.call_llm(prompt, max_tokens=4000)
        
        return {
            "type": doc_type,
            "content": result,
            "agent": self.name
        }


@register_agent("CodeReviewAI")
class CodeReviewAgent(LLMPluginBase):
    """
    Custom agent for code review and quality analysis.
    """
    
    def __init__(self):
        super().__init__(
            name="CodeReviewAI",
            role="Senior Code Reviewer - Analyzes code quality, security, and best practices",
            capabilities=[
                "Code quality analysis",
                "Security vulnerability detection",
                "Performance suggestions",
                "Best practices review",
                "Refactoring recommendations"
            ]
        )
    
    def get_system_prompt(self) -> str:
        return """You are CodeReviewAI, a senior code reviewer with expertise in multiple programming languages.

Review code for:
1. Code Quality: Readability, maintainability, DRY principles
2. Security: Common vulnerabilities, input validation, authentication
3. Performance: Efficiency, resource usage, optimization opportunities
4. Best Practices: Language-specific conventions, design patterns
5. Testing: Test coverage suggestions, edge cases

Provide constructive, actionable feedback with specific line references and examples."""
    
    def process(self, task: Any, context: Any) -> Dict[str, Any]:
        """Review code and provide feedback."""
        code = getattr(task, 'code', '')
        language = getattr(task, 'language', 'python')
        
        prompt = f"""Review this {language} code:

```{language}
{code}
```

Provide:
1. Summary of findings
2. Critical issues (must fix)
3. Recommendations (should fix)
4. Suggestions (nice to have)
5. Overall quality score (1-10)
"""
        
        result = self.call_llm(prompt, max_tokens=3000)
        
        return {
            "review": result,
            "agent": self.name
        }


# ══════════════════════════════════════════════════════════════════════════════
# EXAMPLE: Hooks
# ══════════════════════════════════════════════════════════════════════════════

@register_hook("post_generation")
def add_timestamp_to_readme(context: Any) -> None:
    """
    Example hook that runs after project generation.
    Adds a generation timestamp to the README.
    """
    import os
    from datetime import datetime
    
    if hasattr(context, 'project_dir'):
        readme_path = os.path.join(context.project_dir, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n---\n*Generated by KARYA AGENT on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")


@register_hook("pre_generation")
def validate_project_name(context: Any) -> None:
    """
    Example hook that runs before project generation.
    Validates the project name.
    """
    if hasattr(context, 'project_name'):
        name = context.project_name
        # Simple validation
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            if char in name:
                raise ValueError(f"Project name contains invalid character: {char}")


# ══════════════════════════════════════════════════════════════════════════════
# HOW TO USE
# ══════════════════════════════════════════════════════════════════════════════

"""
To create your own custom agent:

1. Create a new file in the plugins/ directory (e.g., my_agent.py)

2. Import the necessary components:
   from plugins import register_agent
   from plugins.base_plugin import LLMPluginBase  # or PluginBase, ToolPluginBase
   
3. Create your agent class with the @register_agent decorator:
   @register_agent("MyAgentName")
   class MyAgent(LLMPluginBase):
       def __init__(self):
           super().__init__(
               name="MyAgentName",
               role="Description of what this agent does",
               capabilities=["capability1", "capability2"]
           )
       
       def process(self, task, context):
           # Your processing logic here
           return {"result": "..."}

4. Your agent will be automatically loaded when the plugin system initializes!

To use hooks:
   @register_hook("post_generation")  # or "pre_generation", "pre_agent", "post_agent"
   def my_hook(context):
       # Your hook logic here
       pass
"""
