# GenAI Code Review Assistant

An advanced AI-powered code review helper using static analysis. The script analyzes code for issues like complexity, naming conventions, security vulnerabilities, and provides actionable suggestions.

```mermaid
flowchart TD
    File[Source File] --> Parser[Code Parser]
    Parser --> Checks[Analysis Checks]
    Checks --> Issues[Issues Detected]
    Checks --> Suggestions[Suggestions Generated]

    Checks --> LineLength[Line Length Check]
    Checks --> TodoCheck[TODO/FIXME Check]
    Checks --> SecurityCheck[Security Scan]
    Checks --> ComplexityCheck[Complexity Analysis]
    Checks --> NamingCheck[Naming Conventions]
    Checks --> ImportCheck[Import Validation]

    LineLength --> Issues
    TodoCheck --> Issues
    SecurityCheck --> Issues
    ComplexityCheck --> Issues
    NamingCheck --> Issues
    ImportCheck --> Issues

    Issues --> Report[Review Report]
    Suggestions --> Report

    Report --> User[Developer Feedback]
```

## 📂 Structure

```
genai-code-review-assistant/
├── README.md
├── requirements.txt
├── scripts/
│   └── review.py  # Comprehensive code analyzer with AST parsing
```

## 🚀 Usage

```bash
python scripts/review.py path/to/file.py
```

Analyzes Python files for code quality, security, and best practices.

## 🏗️ Analysis Features

- **Syntax Validation**: AST-based parsing for Python files
- **Code Complexity**: Function/class size checks
- **Naming Conventions**: Enforces snake_case/PascalCase
- **Security Scanning**: Detects potential vulnerabilities
- **Import Analysis**: Identifies unused imports
- **Line Length & TODO Checks**: Basic style validation

## 📜 License

MIT License
