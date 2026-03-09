
#!/usr/bin/env python3

import sys
import ast
import re
from typing import List, Dict

class CodeReviewer:
    def __init__(self):
        self.issues = []
        self.suggestions = []

    def analyze_file(self, filename: str):
        print(f"🤖 AI Code Review for {filename}...")
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            self.issues.append(f"Error reading file: {e}")
            return

        if not content.strip():
            self.issues.append("File is empty")
            return

        # Basic checks
        self.check_line_lengths(lines)
        self.check_todos_fixmes(lines)
        self.check_security_issues(content)

        # Python-specific checks
        if filename.endswith('.py'):
            self.analyze_python_code(content, lines)

        # Generate suggestions
        self.generate_suggestions()

    def check_line_lengths(self, lines: List[str]):
        for idx, line in enumerate(lines, start=1):
            if len(line) > 120:
                self.issues.append(f"Line {idx}: exceeds 120 characters ({len(line)})")

    def check_todos_fixmes(self, lines: List[str]):
        for idx, line in enumerate(lines, start=1):
            if "TODO" in line.upper() or "FIXME" in line.upper():
                self.issues.append(f"Line {idx}: contains TODO/FIXME - consider resolving")

    def check_security_issues(self, content: str):
        # Simple security checks
        if "password" in content.lower() and "hardcoded" not in content.lower():
            self.issues.append("Potential hardcoded password detected")
        if "eval(" in content:
            self.issues.append("Use of eval() - security risk")
        if "exec(" in content:
            self.issues.append("Use of exec() - security risk")

    def analyze_python_code(self, content: str, lines: List[str]):
        try:
            tree = ast.parse(content)
            self.check_complexity(tree)
            self.check_naming(tree)
            self.check_imports(tree)
        except SyntaxError as e:
            self.issues.append(f"Syntax error: {e}")

    def check_complexity(self, tree: ast.AST):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 20:
                    self.issues.append(f"Function '{node.name}' is too long ({len(node.body)} statements)")
            elif isinstance(node, ast.ClassDef):
                if len(node.body) > 15:
                    self.issues.append(f"Class '{node.name}' has too many methods/attributes")

    def check_naming(self, tree: ast.AST):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    self.issues.append(f"Function '{node.name}' doesn't follow snake_case")
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    self.issues.append(f"Class '{node.name}' doesn't follow PascalCase")

    def check_imports(self, tree: ast.AST):
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        unused_patterns = ['os', 'sys', 'json']  # Common potentially unused
        for imp in imports:
            if any(pattern in imp for pattern in unused_patterns):
                if imp not in [n.id for n in ast.walk(tree) if isinstance(n, ast.Name)]:
                    self.suggestions.append(f"Consider removing unused import: {imp}")

    def generate_suggestions(self):
        if not self.issues:
            self.suggestions.append("Code looks clean! Consider adding docstrings for better documentation.")
        else:
            self.suggestions.append("Address the issues above to improve code quality.")
            self.suggestions.append("Consider using a linter like flake8 or pylint for automated checks.")

    def report(self):
        if self.issues:
            print("🔍 Issues Found:")
            for issue in self.issues:
                print(f"  - {issue}")
        else:
            print("✅ No major issues detected!")

        if self.suggestions:
            print("\n💡 Suggestions:")
            for suggestion in self.suggestions:
                print(f"  - {suggestion}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/review.py <file_to_review>")
        sys.exit(1)
    filename = sys.argv[1]
    reviewer = CodeReviewer()
    reviewer.analyze_file(filename)
    reviewer.report()
