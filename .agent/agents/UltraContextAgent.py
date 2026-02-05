"""
╔════════════════════════════════════════════════════════════════════════════════╗
║                        ULTRA CONTEXT AGENT                                     ║
║              Extended Context Processing for Large Codebases                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

This agent handles scenarios requiring extended context windows:
- Large codebase analysis
- Multi-file understanding
- Complex documentation synthesis
- Cross-reference generation

It uses techniques like:
- Chunking and summarization
- Hierarchical context building
- Semantic search for relevant context

Author: KARYA AGENT System
Version: 1.0.0
"""

import os
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path

# Optional imports
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")

# Models with large context windows
CONTEXT_MODELS = {
    "ultra": "google/gemini-2.0-flash-001",     # 1M tokens
    "large": "anthropic/claude-3-5-sonnet",      # 200K tokens
    "standard": "openai/gpt-4o",                 # 128K tokens
}

# File type configurations
CODE_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript", 
    ".ts": "typescript",
    ".jsx": "javascript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".cpp": "cpp",
    ".c": "c",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
}

DOC_EXTENSIONS = {".md", ".txt", ".rst", ".adoc"}
CONFIG_EXTENSIONS = {".json", ".yaml", ".yml", ".toml", ".ini", ".env"}


# ══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class FileContext:
    """Represents a file in the context."""
    path: str
    content: str
    language: str
    size: int
    summary: Optional[str] = None
    
    def to_context_string(self, include_content: bool = True) -> str:
        """Convert to a context-friendly string."""
        header = f"# File: {self.path} ({self.language})\n"
        if self.summary and not include_content:
            return header + f"Summary: {self.summary}\n"
        return header + f"```{self.language}\n{self.content}\n```\n"


@dataclass  
class ContextChunk:
    """A chunk of context for processing."""
    chunk_id: str
    content: str
    source_files: List[str]
    token_estimate: int
    

# ══════════════════════════════════════════════════════════════════════════════
# CONTEXT BUILDER
# ══════════════════════════════════════════════════════════════════════════════

class ContextBuilder:
    """
    Builds and manages context from multiple sources.
    Handles large codebases by chunking and summarizing.
    """
    
    def __init__(self, max_tokens: int = 100000):
        """
        Initialize the context builder.
        
        Args:
            max_tokens: Maximum tokens for context window
        """
        self.max_tokens = max_tokens
        self.files: List[FileContext] = []
        self.chunks: List[ContextChunk] = []
        
    def add_file(self, file_path: str) -> bool:
        """
        Add a file to the context.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file was added successfully
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return False
                
            ext = path.suffix.lower()
            language = CODE_EXTENSIONS.get(ext, "text")
            
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            file_ctx = FileContext(
                path=str(path),
                content=content,
                language=language,
                size=len(content)
            )
            self.files.append(file_ctx)
            return True
            
        except Exception as e:
            print(f"Error adding file {file_path}: {e}")
            return False
    
    def add_directory(self, dir_path: str, 
                      extensions: List[str] = None,
                      ignore_patterns: List[str] = None) -> int:
        """
        Add all relevant files from a directory.
        
        Args:
            dir_path: Directory path
            extensions: File extensions to include
            ignore_patterns: Patterns to ignore
            
        Returns:
            Number of files added
        """
        if extensions is None:
            extensions = list(CODE_EXTENSIONS.keys()) + list(DOC_EXTENSIONS) + list(CONFIG_EXTENSIONS)
        
        if ignore_patterns is None:
            ignore_patterns = [
                "node_modules", "__pycache__", ".git", ".venv",
                "venv", "dist", "build", ".next", "coverage"
            ]
        
        count = 0
        for root, dirs, files in os.walk(dir_path):
            # Filter directories
            dirs[:] = [d for d in dirs if not any(p in d for p in ignore_patterns)]
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    if self.add_file(file_path):
                        count += 1
        
        return count
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        return len(text) // 4  # Rough estimate: 4 chars per token
    
    def build_chunks(self, chunk_size: int = 50000) -> List[ContextChunk]:
        """
        Build context chunks from files.
        
        Args:
            chunk_size: Target token size per chunk
            
        Returns:
            List of context chunks
        """
        self.chunks = []
        current_content = ""
        current_files = []
        current_tokens = 0
        chunk_num = 0
        
        for file_ctx in self.files:
            file_str = file_ctx.to_context_string()
            file_tokens = self.estimate_tokens(file_str)
            
            if current_tokens + file_tokens > chunk_size and current_content:
                # Save current chunk
                chunk_id = f"chunk_{chunk_num:03d}"
                self.chunks.append(ContextChunk(
                    chunk_id=chunk_id,
                    content=current_content,
                    source_files=current_files.copy(),
                    token_estimate=current_tokens
                ))
                current_content = ""
                current_files = []
                current_tokens = 0
                chunk_num += 1
            
            current_content += file_str + "\n"
            current_files.append(file_ctx.path)
            current_tokens += file_tokens
        
        # Save remaining content
        if current_content:
            chunk_id = f"chunk_{chunk_num:03d}"
            self.chunks.append(ContextChunk(
                chunk_id=chunk_id,
                content=current_content,
                source_files=current_files,
                token_estimate=current_tokens
            ))
        
        return self.chunks
    
    def get_context_summary(self) -> str:
        """Get a summary of the current context."""
        total_files = len(self.files)
        total_size = sum(f.size for f in self.files)
        total_tokens = sum(self.estimate_tokens(f.content) for f in self.files)
        
        languages = {}
        for f in self.files:
            languages[f.language] = languages.get(f.language, 0) + 1
        
        summary = f"""Context Summary:
- Total Files: {total_files}
- Total Size: {total_size:,} bytes
- Estimated Tokens: {total_tokens:,}
- Languages: {dict(languages)}
"""
        return summary


# ══════════════════════════════════════════════════════════════════════════════
# ULTRA CONTEXT AGENT
# ══════════════════════════════════════════════════════════════════════════════

class UltraContextAgent:
    """
    Agent for processing large contexts and generating comprehensive outputs.
    """
    
    def __init__(self, api_key: str = None, model_tier: str = "ultra"):
        """
        Initialize the agent.
        
        Args:
            api_key: OpenRouter API key
            model_tier: Model tier (ultra, large, standard)
        """
        self.api_key = api_key or DEFAULT_API_KEY
        self.model = CONTEXT_MODELS.get(model_tier, CONTEXT_MODELS["ultra"])
        self.context_builder = ContextBuilder()
        
        if OPENAI_AVAILABLE:
            self.client = OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=self.api_key
            )
        else:
            self.client = None
    
    def _call_llm(self, prompt: str, system_prompt: str = None) -> str:
        """Make an LLM API call."""
        if not self.client:
            return "Error: OpenAI package not installed"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=8000
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_codebase(self, directory: str) -> Dict[str, Any]:
        """
        Perform comprehensive codebase analysis.
        
        Args:
            directory: Root directory of the codebase
            
        Returns:
            Analysis results
        """
        print(f"\n📂 Scanning directory: {directory}")
        files_added = self.context_builder.add_directory(directory)
        print(f"📄 Found {files_added} files")
        
        print(self.context_builder.get_context_summary())
        
        # Build chunks
        chunks = self.context_builder.build_chunks()
        print(f"📦 Created {len(chunks)} context chunks")
        
        # Analyze each chunk
        analyses = []
        for i, chunk in enumerate(chunks):
            print(f"🔍 Analyzing chunk {i+1}/{len(chunks)}...")
            
            prompt = f"""Analyze this portion of the codebase and provide:
1. Main components and their purposes
2. Key patterns and architectural decisions
3. Dependencies and integrations
4. Potential issues or improvements

Codebase Content:
{chunk.content}

Provide a structured analysis."""

            analysis = self._call_llm(prompt)
            analyses.append({
                "chunk_id": chunk.chunk_id,
                "files": chunk.source_files,
                "analysis": analysis
            })
        
        # Synthesize final report
        print("📝 Synthesizing final report...")
        synthesis_prompt = f"""Based on these individual analyses of different parts of the codebase,
create a comprehensive codebase report:

{json.dumps(analyses, indent=2)}

Include:
1. Executive Summary
2. Architecture Overview
3. Key Components
4. Technology Stack
5. Code Quality Assessment
6. Recommendations"""

        final_report = self._call_llm(synthesis_prompt)
        
        return {
            "directory": directory,
            "files_analyzed": files_added,
            "chunks_processed": len(chunks),
            "individual_analyses": analyses,
            "final_report": final_report,
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_documentation(self, directory: str, doc_type: str = "readme") -> str:
        """
        Generate documentation for a codebase.
        
        Args:
            directory: Codebase directory
            doc_type: Type of documentation (readme, api, architecture)
            
        Returns:
            Generated documentation
        """
        self.context_builder.add_directory(directory)
        chunks = self.context_builder.build_chunks()
        
        # Combine all content (may need summarization for very large codebases)
        full_context = "\n".join(c.content for c in chunks[:3])  # Limit to first 3 chunks
        
        prompts = {
            "readme": "Generate a comprehensive README.md for this project.",
            "api": "Generate API documentation for this codebase.",
            "architecture": "Generate an architecture documentation describing the system design."
        }
        
        prompt = f"""{prompts.get(doc_type, prompts['readme'])}

Codebase:
{full_context}

Generate professional, comprehensive documentation."""

        return self._call_llm(prompt)
    
    def answer_question(self, directory: str, question: str) -> str:
        """
        Answer a question about the codebase.
        
        Args:
            directory: Codebase directory
            question: User's question
            
        Returns:
            Answer based on codebase analysis
        """
        self.context_builder.add_directory(directory)
        chunks = self.context_builder.build_chunks()
        
        # Use first chunks for context
        context = "\n".join(c.content for c in chunks[:2])
        
        prompt = f"""Based on this codebase, answer the following question:

Question: {question}

Codebase:
{context}

Provide a detailed, accurate answer based on the code."""

        return self._call_llm(prompt)


# ══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

def print_banner():
    """Print agent banner."""
    print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                                                                                ║
║   ██╗   ██╗██╗  ████████╗██████╗  █████╗      ██████╗ ██████╗ ███╗   ██╗      ║
║   ██║   ██║██║  ╚══██╔══╝██╔══██╗██╔══██╗    ██╔════╝██╔═══██╗████╗  ██║      ║
║   ██║   ██║██║     ██║   ██████╔╝███████║    ██║     ██║   ██║██╔██╗ ██║      ║
║   ██║   ██║██║     ██║   ██╔══██╗██╔══██║    ██║     ██║   ██║██║╚██╗██║      ║
║   ╚██████╔╝███████╗██║   ██║  ██║██║  ██║    ╚██████╗╚██████╔╝██║ ╚████║      ║
║    ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝     ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝      ║
║                                                                                ║
║                    🧠 Extended Context AI Agent                                 ║
║                                                                                ║
╚════════════════════════════════════════════════════════════════════════════════╝
    """)


def main():
    """Main CLI entry point."""
    print_banner()
    
    agent = UltraContextAgent()
    
    print("\n🎯 Select an option:")
    print("   1. Analyze Codebase")
    print("   2. Generate Documentation")
    print("   3. Ask Question About Codebase")
    print("   4. Exit")
    
    while True:
        choice = input("\n>>> ").strip()
        
        if choice == "1":
            directory = input("Enter directory path: ").strip()
            result = agent.analyze_codebase(directory)
            print("\n" + "═" * 70)
            print("📊 ANALYSIS REPORT")
            print("═" * 70)
            print(result["final_report"])
            
        elif choice == "2":
            directory = input("Enter directory path: ").strip()
            doc_type = input("Doc type (readme/api/architecture): ").strip() or "readme"
            docs = agent.generate_documentation(directory, doc_type)
            print("\n" + "═" * 70)
            print(f"📚 GENERATED {doc_type.upper()}")
            print("═" * 70)
            print(docs)
            
        elif choice == "3":
            directory = input("Enter directory path: ").strip()
            question = input("Your question: ").strip()
            answer = agent.answer_question(directory, question)
            print("\n" + "═" * 70)
            print("💡 ANSWER")
            print("═" * 70)
            print(answer)
            
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        else:
            print("Invalid option. Please choose 1-4.")


if __name__ == "__main__":
    main()