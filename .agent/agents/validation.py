"""
KARYA AGENT - Validation Pipeline
═══════════════════════════════════════════════════════════════════════════════

Automatic quality validation for generated projects.
Pre-checks (before generation) and post-checks (after generation).

Usage:
    from validation import ValidationPipeline, run_validation
    
    pipeline = ValidationPipeline()
    results = pipeline.run_post_checks(project_dir)
    print(results.summary())

Version: 1.0.0
"""

import os
import subprocess
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class CheckStatus(Enum):
    """Validation check status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"


class CheckCategory(Enum):
    """Validation check categories."""
    STRUCTURE = "structure"
    CODE = "code"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"
    SECURITY = "security"
    DEVOPS = "devops"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    name: str
    status: CheckStatus
    category: CheckCategory
    message: str
    details: Optional[str] = None
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationReport:
    """Complete validation report."""
    project_dir: str
    results: List[ValidationResult] = field(default_factory=list)
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    skipped: int = 0
    
    def add_result(self, result: ValidationResult):
        """Add a validation result."""
        self.results.append(result)
        if result.status == CheckStatus.PASSED:
            self.passed += 1
        elif result.status == CheckStatus.FAILED:
            self.failed += 1
        elif result.status == CheckStatus.WARNING:
            self.warnings += 1
        else:
            self.skipped += 1
    
    @property
    def success(self) -> bool:
        """Check if all critical validations passed."""
        return self.failed == 0
    
    @property
    def score(self) -> float:
        """Calculate validation score (0-100)."""
        total = self.passed + self.failed + self.warnings
        if total == 0:
            return 100.0
        return (self.passed / total) * 100
    
    def summary(self) -> str:
        """Generate summary report."""
        lines = []
        lines.append("\n" + "=" * 60)
        lines.append("📋 VALIDATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Project: {self.project_dir}")
        lines.append(f"\nScore: {self.score:.1f}%")
        lines.append(f"  ✅ Passed:   {self.passed}")
        lines.append(f"  ❌ Failed:   {self.failed}")
        lines.append(f"  ⚠️  Warnings: {self.warnings}")
        lines.append(f"  ⏭️  Skipped:  {self.skipped}")
        
        if self.failed > 0:
            lines.append("\n❌ FAILURES:")
            for r in self.results:
                if r.status == CheckStatus.FAILED:
                    lines.append(f"  • [{r.category.value}] {r.name}: {r.message}")
        
        if self.warnings > 0:
            lines.append("\n⚠️  WARNINGS:")
            for r in self.results:
                if r.status == CheckStatus.WARNING:
                    lines.append(f"  • [{r.category.value}] {r.name}: {r.message}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "project_dir": self.project_dir,
            "score": self.score,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
            "skipped": self.skipped,
            "results": [
                {
                    "name": r.name,
                    "status": r.status.value,
                    "category": r.category.value,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ]
        }


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION CHECKS
# ══════════════════════════════════════════════════════════════════════════════

class ValidationChecks:
    """Collection of validation check functions."""
    
    @staticmethod
    def check_readme_exists(project_dir: str) -> ValidationResult:
        """Check if README.md exists."""
        readme_path = Path(project_dir) / "README.md"
        if readme_path.exists():
            size = readme_path.stat().st_size
            if size > 500:
                return ValidationResult(
                    name="README.md exists",
                    status=CheckStatus.PASSED,
                    category=CheckCategory.DOCUMENTATION,
                    message=f"README.md found ({size} bytes)"
                )
            else:
                return ValidationResult(
                    name="README.md exists",
                    status=CheckStatus.WARNING,
                    category=CheckCategory.DOCUMENTATION,
                    message="README.md is too short",
                    severity="warning"
                )
        return ValidationResult(
            name="README.md exists",
            status=CheckStatus.FAILED,
            category=CheckCategory.DOCUMENTATION,
            message="README.md not found"
        )
    
    @staticmethod
    def check_code_directory(project_dir: str) -> ValidationResult:
        """Check if code directory exists."""
        code_dir = Path(project_dir) / "10_Code"
        if code_dir.exists() and code_dir.is_dir():
            # Count files
            file_count = sum(1 for _ in code_dir.rglob("*") if _.is_file())
            if file_count > 0:
                return ValidationResult(
                    name="Code directory",
                    status=CheckStatus.PASSED,
                    category=CheckCategory.STRUCTURE,
                    message=f"10_Code/ found with {file_count} files"
                )
            else:
                return ValidationResult(
                    name="Code directory",
                    status=CheckStatus.WARNING,
                    category=CheckCategory.STRUCTURE,
                    message="10_Code/ is empty",
                    severity="warning"
                )
        return ValidationResult(
            name="Code directory",
            status=CheckStatus.FAILED,
            category=CheckCategory.STRUCTURE,
            message="10_Code/ directory not found"
        )
    
    @staticmethod
    def check_dockerfile(project_dir: str) -> ValidationResult:
        """Check if Dockerfile exists."""
        dockerfile = Path(project_dir) / "Dockerfile"
        compose = Path(project_dir) / "docker-compose.yml"
        
        if dockerfile.exists() or compose.exists():
            return ValidationResult(
                name="Docker configuration",
                status=CheckStatus.PASSED,
                category=CheckCategory.DEVOPS,
                message="Docker configuration found"
            )
        
        # Check in subdirectories
        dockerfiles = list(Path(project_dir).rglob("Dockerfile*"))
        if dockerfiles:
            return ValidationResult(
                name="Docker configuration",
                status=CheckStatus.PASSED,
                category=CheckCategory.DEVOPS,
                message=f"Found {len(dockerfiles)} Dockerfile(s)"
            )
        
        return ValidationResult(
            name="Docker configuration",
            status=CheckStatus.WARNING,
            category=CheckCategory.DEVOPS,
            message="No Docker configuration found",
            severity="warning"
        )
    
    @staticmethod
    def check_requirements(project_dir: str) -> ValidationResult:
        """Check if requirements file exists."""
        req_files = [
            "requirements.txt",
            "pyproject.toml",
            "package.json",
            "Pipfile",
            "setup.py"
        ]
        
        found = []
        for req in req_files:
            # Check root
            if (Path(project_dir) / req).exists():
                found.append(req)
            # Check in subdirs
            for f in Path(project_dir).rglob(req):
                if str(f.name) not in found:
                    found.append(str(f.relative_to(project_dir)))
        
        if found:
            return ValidationResult(
                name="Dependency files",
                status=CheckStatus.PASSED,
                category=CheckCategory.CONFIGURATION,
                message=f"Found: {', '.join(found[:3])}"
            )
        
        return ValidationResult(
            name="Dependency files",
            status=CheckStatus.WARNING,
            category=CheckCategory.CONFIGURATION,
            message="No dependency file found",
            severity="warning"
        )
    
    @staticmethod
    def check_tests_exist(project_dir: str) -> ValidationResult:
        """Check if test files exist."""
        test_patterns = ["test_*.py", "*_test.py", "*.test.js", "*.spec.js", "*.test.ts"]
        
        test_files = []
        for pattern in test_patterns:
            test_files.extend(Path(project_dir).rglob(pattern))
        
        if test_files:
            return ValidationResult(
                name="Test files",
                status=CheckStatus.PASSED,
                category=CheckCategory.CODE,
                message=f"Found {len(test_files)} test file(s)"
            )
        
        return ValidationResult(
            name="Test files",
            status=CheckStatus.WARNING,
            category=CheckCategory.CODE,
            message="No test files found",
            severity="warning"
        )
    
    @staticmethod
    def check_gitignore(project_dir: str) -> ValidationResult:
        """Check if .gitignore exists."""
        gitignore = Path(project_dir) / ".gitignore"
        
        if gitignore.exists():
            return ValidationResult(
                name=".gitignore",
                status=CheckStatus.PASSED,
                category=CheckCategory.CONFIGURATION,
                message=".gitignore found"
            )
        
        return ValidationResult(
            name=".gitignore",
            status=CheckStatus.WARNING,
            category=CheckCategory.CONFIGURATION,
            message=".gitignore not found",
            severity="warning"
        )
    
    @staticmethod
    def check_architecture_doc(project_dir: str) -> ValidationResult:
        """Check if architecture documentation exists."""
        arch_file = Path(project_dir) / "03_Architecture.md"
        
        if arch_file.exists():
            size = arch_file.stat().st_size
            if size > 1000:
                return ValidationResult(
                    name="Architecture documentation",
                    status=CheckStatus.PASSED,
                    category=CheckCategory.DOCUMENTATION,
                    message=f"03_Architecture.md found ({size} bytes)"
                )
            else:
                return ValidationResult(
                    name="Architecture documentation",
                    status=CheckStatus.WARNING,
                    category=CheckCategory.DOCUMENTATION,
                    message="Architecture doc is sparse",
                    severity="warning"
                )
        
        return ValidationResult(
            name="Architecture documentation",
            status=CheckStatus.WARNING,
            category=CheckCategory.DOCUMENTATION,
            message="03_Architecture.md not found",
            severity="warning"
        )
    
    @staticmethod
    def check_env_example(project_dir: str) -> ValidationResult:
        """Check if .env.example exists."""
        env_example = Path(project_dir) / ".env.example"
        env_sample = Path(project_dir) / ".env.sample"
        
        if env_example.exists() or env_sample.exists():
            return ValidationResult(
                name="Environment template",
                status=CheckStatus.PASSED,
                category=CheckCategory.SECURITY,
                message=".env.example found"
            )
        
        # Check if any .env exists (potential security issue)
        env_file = Path(project_dir) / ".env"
        if env_file.exists():
            return ValidationResult(
                name="Environment template",
                status=CheckStatus.WARNING,
                category=CheckCategory.SECURITY,
                message=".env exists but no .env.example template",
                severity="warning"
            )
        
        return ValidationResult(
            name="Environment template",
            status=CheckStatus.SKIPPED,
            category=CheckCategory.SECURITY,
            message="No .env configuration needed"
        )
    
    @staticmethod
    def check_sensitive_data(project_dir: str) -> ValidationResult:
        """Check for hardcoded sensitive data."""
        sensitive_patterns = [
            "password=", "api_key=", "secret=", "token=",
            "sk-", "Bearer ", "AWS_SECRET"
        ]
        
        issues = []
        code_files = []
        for ext in ["*.py", "*.js", "*.ts", "*.yaml", "*.yml", "*.json"]:
            code_files.extend(Path(project_dir).rglob(ext))
        
        for file_path in code_files[:50]:  # Limit for performance
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                for pattern in sensitive_patterns:
                    if pattern.lower() in content.lower():
                        # Skip if it's in .example or template files
                        if ".example" not in str(file_path) and "template" not in str(file_path).lower():
                            issues.append(f"{file_path.name}: potential {pattern}")
                            break
            except:
                pass
        
        if issues:
            return ValidationResult(
                name="Sensitive data check",
                status=CheckStatus.WARNING,
                category=CheckCategory.SECURITY,
                message=f"Found {len(issues)} potential issues",
                details="; ".join(issues[:3]),
                severity="warning"
            )
        
        return ValidationResult(
            name="Sensitive data check",
            status=CheckStatus.PASSED,
            category=CheckCategory.SECURITY,
            message="No obvious sensitive data found"
        )


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

class ValidationPipeline:
    """Orchestrates validation checks."""
    
    def __init__(self):
        self.checks = ValidationChecks()
        
        # Default check functions
        self.post_checks = [
            self.checks.check_readme_exists,
            self.checks.check_code_directory,
            self.checks.check_dockerfile,
            self.checks.check_requirements,
            self.checks.check_tests_exist,
            self.checks.check_gitignore,
            self.checks.check_architecture_doc,
            self.checks.check_env_example,
            self.checks.check_sensitive_data,
        ]
        
        self.pre_checks: List[Callable] = []
    
    def add_check(self, check_func: Callable, pre: bool = False):
        """Add a custom check function."""
        if pre:
            self.pre_checks.append(check_func)
        else:
            self.post_checks.append(check_func)
    
    def run_pre_checks(self, config: Dict[str, Any]) -> ValidationReport:
        """Run pre-generation checks."""
        report = ValidationReport(project_dir="pre-generation")
        
        # Check API key
        api_key = os.getenv("OPENROUTER_API_KEY", config.get("api_key", ""))
        if api_key and len(api_key) > 10:
            report.add_result(ValidationResult(
                name="API Key",
                status=CheckStatus.PASSED,
                category=CheckCategory.CONFIGURATION,
                message="API key configured"
            ))
        else:
            report.add_result(ValidationResult(
                name="API Key",
                status=CheckStatus.FAILED,
                category=CheckCategory.CONFIGURATION,
                message="API key not configured"
            ))
        
        # Check output directory
        output_dir = config.get("output_dir", "projects")
        if os.path.exists(output_dir) or os.access(os.path.dirname(output_dir) or ".", os.W_OK):
            report.add_result(ValidationResult(
                name="Output directory",
                status=CheckStatus.PASSED,
                category=CheckCategory.CONFIGURATION,
                message=f"Output directory accessible: {output_dir}"
            ))
        else:
            report.add_result(ValidationResult(
                name="Output directory",
                status=CheckStatus.WARNING,
                category=CheckCategory.CONFIGURATION,
                message="Output directory may not be writable",
                severity="warning"
            ))
        
        # Run custom pre-checks
        for check in self.pre_checks:
            try:
                result = check(config)
                report.add_result(result)
            except Exception as e:
                logger.error(f"Pre-check error: {e}")
        
        return report
    
    def run_post_checks(self, project_dir: str) -> ValidationReport:
        """Run post-generation checks."""
        report = ValidationReport(project_dir=project_dir)
        
        if not os.path.exists(project_dir):
            report.add_result(ValidationResult(
                name="Project directory",
                status=CheckStatus.FAILED,
                category=CheckCategory.STRUCTURE,
                message=f"Project directory not found: {project_dir}"
            ))
            return report
        
        for check in self.post_checks:
            try:
                result = check(project_dir)
                report.add_result(result)
            except Exception as e:
                logger.error(f"Post-check error: {e}")
                report.add_result(ValidationResult(
                    name=check.__name__,
                    status=CheckStatus.FAILED,
                    category=CheckCategory.CODE,
                    message=f"Check failed: {str(e)}"
                ))
        
        return report
    
    def run_all(self, project_dir: str, config: Dict[str, Any] = None) -> Dict[str, ValidationReport]:
        """Run both pre and post checks."""
        return {
            "pre": self.run_pre_checks(config or {}),
            "post": self.run_post_checks(project_dir)
        }


# ══════════════════════════════════════════════════════════════════════════════
# QUALITY GATES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class QualityGate:
    """Quality gate configuration."""
    name: str
    min_score: float = 70.0
    max_failures: int = 0
    max_warnings: int = 5
    required_checks: List[str] = field(default_factory=list)
    
    def evaluate(self, report: ValidationReport) -> bool:
        """Evaluate if quality gate is passed."""
        if report.failed > self.max_failures:
            return False
        if report.warnings > self.max_warnings:
            return False
        if report.score < self.min_score:
            return False
        
        # Check required checks passed
        for req in self.required_checks:
            found = False
            for result in report.results:
                if result.name == req and result.status == CheckStatus.PASSED:
                    found = True
                    break
            if not found:
                return False
        
        return True


# Default quality gates
QUALITY_GATES = {
    "basic": QualityGate(
        name="Basic",
        min_score=50.0,
        max_failures=2,
        max_warnings=10
    ),
    "standard": QualityGate(
        name="Standard",
        min_score=70.0,
        max_failures=0,
        max_warnings=5,
        required_checks=["README.md exists", "Code directory"]
    ),
    "strict": QualityGate(
        name="Strict",
        min_score=90.0,
        max_failures=0,
        max_warnings=2,
        required_checks=[
            "README.md exists",
            "Code directory",
            "Docker configuration",
            "Test files"
        ]
    )
}


# ══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def run_validation(project_dir: str, quality_gate: str = "standard") -> Dict[str, Any]:
    """Run validation and return results."""
    pipeline = ValidationPipeline()
    report = pipeline.run_post_checks(project_dir)
    
    gate = QUALITY_GATES.get(quality_gate, QUALITY_GATES["standard"])
    passed_gate = gate.evaluate(report)
    
    return {
        "report": report,
        "summary": report.summary(),
        "score": report.score,
        "passed_gate": passed_gate,
        "gate_name": gate.name
    }


# ══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        gate = sys.argv[2] if len(sys.argv) > 2 else "standard"
        
        print(f"\n🔍 Validating: {project_path}")
        print(f"   Quality Gate: {gate}")
        
        result = run_validation(project_path, gate)
        print(result["summary"])
        
        if result["passed_gate"]:
            print(f"\n✅ Quality Gate '{result['gate_name']}' PASSED")
        else:
            print(f"\n❌ Quality Gate '{result['gate_name']}' FAILED")
    else:
        print("Usage: python validation.py <project_dir> [quality_gate]")
        print("\nQuality gates: basic, standard, strict")
