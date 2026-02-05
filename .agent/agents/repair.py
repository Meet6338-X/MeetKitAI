import ast
import logging
import sys
import json
from openai import OpenAI
import os

# Configure logging
logger = logging.getLogger("CodeHealer")

class CodeHealer:
    """
    Self-healing mechanism for generated code.
    Checks for syntax errors and attempts to auto-repair using LLM.
    """
    
    def __init__(self, api_key=None, base_url=None, model="google/gemini-2.0-flash-001"):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url or "https://openrouter.ai/api/v1"
        self.model = model
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    def check_syntax(self, file_path: str, content: str) -> tuple[bool, str]:
        """
        Check syntax of the code based on file extension.
        Returns (is_valid, error_message)
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.py':
            try:
                ast.parse(content)
                return True, None
            except SyntaxError as e:
                return False, f"SyntaxError: {e.msg} at line {e.lineno}, offset {e.offset}: {e.text}"
            except Exception as e:
                return False, str(e)
        
        # For JS/TS/Other, we can't easily check syntax without external tools (node, etc.) purely in Python 
        # without heavier dependencies. For now, we trust or assume valid if not Python.
        # Future improvement: subprocess call to `node -c` if node exists.
        
        return True, None

    def heal_code(self, file_path: str, content: str, error_message: str) -> str:
        """
        Attempt to fix the code using LLM.
        """
        prompt = f"""You are an Expert Code Repair Agent.
The following file '{file_path}' has a syntax error.

ERROR:
{error_message}

BROKEN CODE:
```
{content}
```

Task: Fix the syntax error. Return ONLY the full fixed code. Do not wrap in markdown blocks if possible, or strictly use ```code blocks.
Do not add explanations.
"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a code repair tool. Output only valid code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            fixed_code = response.choices[0].message.content
            
            # Clean markdown
            if fixed_code.strip().startswith("```"):
                lines = fixed_code.strip().split("\n")
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                fixed_code = "\n".join(lines)
                
            return fixed_code
        except Exception as e:
            logger.error(f"Heal failed: {e}")
            return content

    def process_file(self, file_path: str, content: str) -> str:
        """
        Full process: Check syntax -> Heal if needed -> Return final content.
        """
        is_valid, error = self.check_syntax(file_path, content)
        
        if not is_valid:
            print(f"   🩹 Healing {os.path.basename(file_path)}... (Error: {error[:50]}...)")
            fixed_content = self.heal_code(file_path, content, error)
            
            # Verify fix
            worked, new_error = self.check_syntax(file_path, fixed_content)
            if worked:
                print(f"   ✨ Healed successfully!")
                return fixed_content
            else:
                print(f"   ⚠️ Healing failed. Saving original with errors.")
                return content # Return original if fix failed to avoid losing data or getting hallucinated garbage
        
        return content
