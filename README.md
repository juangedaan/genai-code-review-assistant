# GenAI Code Review Assistant

An advanced AI-powered code review helper using static analysis. The script analyzes code for issues like complexity, naming conventions, security vulnerabilities, and provides actionable suggestions.

```mermaid
flowchart TD
    PR[GitHub Pull Request] --> Action[GitHub Actions workflow]
    Action -->|git diff| DiffFile[pr.diff]
    Dev[Developer CLI] -->|review.py --diff file.diff| DiffFile
    Dev -->|review.py file.py| Static[Static analysis: AST, complexity, naming, security, imports, style]

    DiffFile --> Key{ANTHROPIC_API_KEY set?}
    Key -->|yes| API[Anthropic API - claude-sonnet-5]
    Key -->|no or --dry-run| Mock[Offline mock review]

    API --> Report[Review report: Issues Found + Suggestions]
    Mock --> Report
    Static --> Report
    Report --> User[Developer feedback]
```

## 📂 Structure

```
genai-code-review-assistant/
├── README.md
├── requirements.txt
├── examples/
│   └── sample.diff        # Sample diff for demoing AI review offline
├── scripts/
│   └── review.py          # Static analyzer (AST) + AI diff reviewer
└── .github/workflows/
    └── genai-review.yml   # Runs the AI review on pull requests
```

## 🚀 Usage

### Static analysis of a file

```bash
python scripts/review.py path/to/file.py
```

Analyzes Python files for code quality, security, and best practices.

### AI review of a diff

```bash
export ANTHROPIC_API_KEY=sk-ant-...          # optional: ANTHROPIC_MODEL (default: claude-sonnet-5)
python scripts/review.py --diff examples/sample.diff
```

Sends the unified diff to the Anthropic API and prints a review with
"Issues Found" and "Suggestions" sections. Without an API key (or with
`--dry-run`) it prints an offline mock review, so the demo works anywhere.
The GitHub Actions workflow runs this automatically on every pull request
using the `ANTHROPIC_API_KEY` repository secret.

## 🏗️ Analysis Features

- **Syntax Validation**: AST-based parsing for Python files
- **Code Complexity**: Function/class size checks
- **Naming Conventions**: Enforces snake_case/PascalCase
- **Security Scanning**: Detects potential vulnerabilities
- **Import Analysis**: Identifies unused imports
- **Line Length & TODO Checks**: Basic style validation

## 📜 License

MIT License
