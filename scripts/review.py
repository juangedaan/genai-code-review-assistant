#!/usr/bin/env python3

import argparse
import ast
import os
import re
import sys
from typing import List

DEFAULT_MODEL = "claude-sonnet-5"

REVIEW_SYSTEM_PROMPT = (
    "You are a senior code reviewer. You are given a unified diff. "
    "Produce a concise review with two sections:\n"
    "🔍 Issues Found: bullet list of concrete problems (bugs, security, style), "
    "or 'None' if clean.\n"
    "💡 Suggestions: bullet list of actionable improvements.\n"
    "Reference file names and line context from the diff. Be brief."
)

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

def summarize_diff(diff_text: str):
    files = re.findall(r'^\+\+\+ b/(.+)$', diff_text, re.MULTILINE)
    added = sum(1 for l in diff_text.splitlines()
                if l.startswith('+') and not l.startswith('+++'))
    removed = sum(1 for l in diff_text.splitlines()
                  if l.startswith('-') and not l.startswith('---'))
    return files, added, removed


def mock_review(diff_text: str) -> str:
    """Deterministic offline review so the demo works without an API key."""
    files, added, removed = summarize_diff(diff_text)
    file_list = ", ".join(files) if files else "(no files detected)"
    return (
        "🔍 Issues Found:\n"
        f"  - [mock] Reviewed {len(files)} file(s): {file_list} "
        f"(+{added}/-{removed} lines). No AI analysis performed in mock mode.\n"
        "\n💡 Suggestions:\n"
        "  - Set ANTHROPIC_API_KEY to get a real AI-generated review.\n"
        "  - Keep diffs small and focused for higher-quality reviews.\n"
    )


def ai_review_diff(diff_text: str, dry_run: bool = False) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if dry_run:
        return mock_review(diff_text)
    if not api_key:
        print("NOTE: ANTHROPIC_API_KEY is not set - no API call will be made.\n"
              "      Falling back to offline mock review (same as --dry-run).\n",
              file=sys.stderr)
        return mock_review(diff_text)

    import anthropic  # imported lazily; static file mode needs no dependencies
    model = os.environ.get("ANTHROPIC_MODEL", DEFAULT_MODEL)
    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model=model,
            max_tokens=16000,
            system=REVIEW_SYSTEM_PROMPT,
            messages=[{
                "role": "user",
                "content": f"Review this diff:\n\n```diff\n{diff_text}\n```",
            }],
        )
    except anthropic.AuthenticationError:
        sys.exit("Error: invalid ANTHROPIC_API_KEY.")
    except anthropic.RateLimitError:
        sys.exit("Error: rate limited by the Anthropic API - retry later.")
    except anthropic.APIStatusError as e:
        sys.exit(f"Error: Anthropic API returned {e.status_code}: {e.message}")
    except anthropic.APIConnectionError:
        sys.exit("Error: could not reach the Anthropic API - check your network.")
    return "".join(b.text for b in response.content if b.type == "text")


def main():
    parser = argparse.ArgumentParser(
        description="GenAI code review: static analysis of a file, "
                    "or AI review of a unified diff.")
    parser.add_argument("target", nargs="?",
                        help="File to statically analyze (e.g. path/to/file.py)")
    parser.add_argument("--diff", metavar="DIFF_FILE",
                        help="Unified diff file to AI-review ('-' for stdin)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Offline mock review of the diff (no API call)")
    args = parser.parse_args()

    if args.diff:
        diff_text = (sys.stdin.read() if args.diff == "-"
                     else open(args.diff, encoding="utf-8").read())
        if not diff_text.strip():
            sys.exit("Error: diff is empty - nothing to review.")
        print("🤖 AI Code Review (diff mode)...\n")
        print(ai_review_diff(diff_text, dry_run=args.dry_run))
    elif args.target:
        reviewer = CodeReviewer()
        reviewer.analyze_file(args.target)
        reviewer.report()
    else:
        parser.print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
