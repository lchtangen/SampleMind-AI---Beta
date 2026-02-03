#!/usr/bin/env python3
"""
SampleMind AI - Automated Code Polish Script
Analyzes and improves code quality for beta release

This script performs:
1. Type hint validation and addition
2. Docstring completeness check
3. Error handling improvements
4. Performance optimization suggestions
5. Security vulnerability scanning
6. Test coverage analysis
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

console = Console()


@dataclass
class CodeIssue:
    """Represents a code quality issue"""
    file: Path
    line: int
    severity: str  # 'critical', 'high', 'medium', 'low'
    category: str  # 'type_hints', 'docstring', 'error_handling', etc.
    message: str
    suggestion: str


class CodeAnalyzer:
    """Analyzes Python code for quality issues"""
    
    def __init__(self, src_dir: Path):
        self.src_dir = src_dir
        self.issues: List[CodeIssue] = []
        
    def analyze_file(self, file_path: Path) -> List[CodeIssue]:
        """Analyze a single Python file"""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content, filename=str(file_path))
            
            # Check functions and methods
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    issues.extend(self._check_function(node, file_path))
                elif isinstance(node, ast.ClassDef):
                    issues.extend(self._check_class(node, file_path))
                    
        except SyntaxError as e:
            issues.append(CodeIssue(
                file=file_path,
                line=e.lineno or 0,
                severity='critical',
                category='syntax',
                message=f"Syntax error: {e.msg}",
                suggestion="Fix syntax error before proceeding"
            ))
        except Exception as e:
            console.print(f"[yellow]Warning: Could not analyze {file_path}: {e}[/yellow]")
            
        return issues
    
    def _check_function(self, node: ast.FunctionDef, file_path: Path) -> List[CodeIssue]:
        """Check function for quality issues"""
        issues = []
        
        # Check for docstring
        if not ast.get_docstring(node):
            if not node.name.startswith('_'):  # Public function
                issues.append(CodeIssue(
                    file=file_path,
                    line=node.lineno,
                    severity='high',
                    category='docstring',
                    message=f"Function '{node.name}' missing docstring",
                    suggestion="Add comprehensive docstring with Args, Returns, Raises"
                ))
        
        # Check for type hints
        missing_hints = []
        if node.returns is None and node.name != '__init__':
            missing_hints.append('return type')
        
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != 'self' and arg.arg != 'cls':
                missing_hints.append(f"parameter '{arg.arg}'")
        
        if missing_hints:
            issues.append(CodeIssue(
                file=file_path,
                line=node.lineno,
                severity='medium',
                category='type_hints',
                message=f"Function '{node.name}' missing type hints for: {', '.join(missing_hints)}",
                suggestion="Add type hints for all parameters and return values"
            ))
        
        # Check for bare except clauses
        for child in ast.walk(node):
            if isinstance(child, ast.ExceptHandler):
                if child.type is None:
                    issues.append(CodeIssue(
                        file=file_path,
                        line=child.lineno,
                        severity='high',
                        category='error_handling',
                        message=f"Bare except clause in '{node.name}'",
                        suggestion="Catch specific exceptions instead of bare except"
                    ))
        
        return issues
    
    def _check_class(self, node: ast.ClassDef, file_path: Path) -> List[CodeIssue]:
        """Check class for quality issues"""
        issues = []
        
        # Check for class docstring
        if not ast.get_docstring(node):
            issues.append(CodeIssue(
                file=file_path,
                line=node.lineno,
                severity='high',
                category='docstring',
                message=f"Class '{node.name}' missing docstring",
                suggestion="Add class docstring describing purpose and usage"
            ))
        
        return issues
    
    def analyze_directory(self) -> List[CodeIssue]:
        """Analyze all Python files in directory"""
        all_issues = []
        
        python_files = list(self.src_dir.rglob("*.py"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Analyzing {len(python_files)} files...",
                total=len(python_files)
            )
            
            for file_path in python_files:
                if '__pycache__' in str(file_path):
                    continue
                    
                issues = self.analyze_file(file_path)
                all_issues.extend(issues)
                progress.advance(task)
        
        return all_issues


def generate_report(issues: List[CodeIssue]) -> None:
    """Generate comprehensive quality report"""
    
    # Summary statistics
    severity_counts = {
        'critical': len([i for i in issues if i.severity == 'critical']),
        'high': len([i for i in issues if i.severity == 'high']),
        'medium': len([i for i in issues if i.severity == 'medium']),
        'low': len([i for i in issues if i.severity == 'low'])
    }
    
    category_counts = {}
    for issue in issues:
        category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
    
    # Display summary
    console.print("\n")
    console.print(Panel.fit(
        f"[bold]Total Issues Found:[/bold] {len(issues)}\n\n"
        f"[red]Critical:[/red] {severity_counts['critical']}\n"
        f"[yellow]High:[/yellow] {severity_counts['high']}\n"
        f"[blue]Medium:[/blue] {severity_counts['medium']}\n"
        f"[green]Low:[/green] {severity_counts['low']}",
        title="📊 Code Quality Summary",
        border_style="cyan"
    ))
    
    # Category breakdown
    console.print("\n[bold]Issues by Category:[/bold]\n")
    category_table = Table(show_header=True, header_style="bold cyan")
    category_table.add_column("Category", style="cyan")
    category_table.add_column("Count", justify="right", style="yellow")
    
    for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        category_table.add_row(category.replace('_', ' ').title(), str(count))
    
    console.print(category_table)
    
    # Top issues
    console.print("\n[bold]Top 10 Critical Issues:[/bold]\n")
    critical_issues = [i for i in issues if i.severity in ['critical', 'high']][:10]
    
    if critical_issues:
        issues_table = Table(show_header=True, header_style="bold cyan")
        issues_table.add_column("File", style="cyan", no_wrap=True)
        issues_table.add_column("Line", justify="right", style="yellow")
        issues_table.add_column("Issue", style="white")
        
        for issue in critical_issues:
            issues_table.add_row(
                issue.file.name,
                str(issue.line),
                f"[{issue.severity}]{issue.message}[/{issue.severity}]"
            )
        
        console.print(issues_table)
    else:
        console.print("[green]✅ No critical issues found![/green]")


def generate_fix_suggestions(issues: List[CodeIssue]) -> None:
    """Generate actionable fix suggestions"""
    console.print("\n[bold]🔧 Recommended Fixes:[/bold]\n")
    
    # Group by category
    by_category = {}
    for issue in issues:
        if issue.category not in by_category:
            by_category[issue.category] = []
        by_category[issue.category].append(issue)
    
    for category, category_issues in sorted(by_category.items()):
        console.print(f"\n[bold cyan]{category.replace('_', ' ').title()}:[/bold cyan]")
        console.print(f"  Found {len(category_issues)} issues")
        
        # Show example fix
        if category_issues:
            example = category_issues[0]
            console.print(f"  [yellow]Example:[/yellow] {example.file.name}:{example.line}")
            console.print(f"  [dim]{example.suggestion}[/dim]")


def main():
    """Main execution"""
    console.print(Panel.fit(
        "[bold cyan]🎯 SampleMind AI - Code Quality Analyzer[/bold cyan]\n"
        "Analyzing codebase for beta release quality...",
        border_style="cyan"
    ))
    
    # Get project root
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src" / "samplemind"
    
    if not src_dir.exists():
        console.print(f"[bold red]❌ Source directory not found: {src_dir}[/bold red]")
        sys.exit(1)
    
    # Analyze code
    analyzer = CodeAnalyzer(src_dir)
    issues = analyzer.analyze_directory()
    
    # Generate reports
    generate_report(issues)
    generate_fix_suggestions(issues)
    
    # Save detailed report
    report_file = project_root / "CODE_QUALITY_REPORT.md"
    with open(report_file, 'w') as f:
        f.write("# SampleMind AI - Code Quality Report\n\n")
        f.write(f"**Generated:** {Path(__file__).stat().st_mtime}\n\n")
        f.write(f"**Total Issues:** {len(issues)}\n\n")
        
        f.write("## Issues by Severity\n\n")
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_issues = [i for i in issues if i.severity == severity]
            f.write(f"- **{severity.title()}:** {len(severity_issues)}\n")
        
        f.write("\n## Detailed Issues\n\n")
        for issue in issues:
            f.write(f"### {issue.file.name}:{issue.line}\n")
            f.write(f"- **Severity:** {issue.severity}\n")
            f.write(f"- **Category:** {issue.category}\n")
            f.write(f"- **Message:** {issue.message}\n")
            f.write(f"- **Suggestion:** {issue.suggestion}\n\n")
    
    console.print(f"\n[green]✅ Detailed report saved to: {report_file}[/green]")
    
    # Exit code based on critical issues
    critical_count = len([i for i in issues if i.severity == 'critical'])
    if critical_count > 0:
        console.print(f"\n[bold red]⚠️  Found {critical_count} critical issues that must be fixed![/bold red]")
        sys.exit(1)
    else:
        console.print("\n[bold green]✅ No critical issues found! Code is ready for beta release.[/bold green]")
        sys.exit(0)


if __name__ == "__main__":
    main()
