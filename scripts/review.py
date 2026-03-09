
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review.py <file_to_review>")
        sys.exit(1)
    filename = sys.argv[1]
    print(f"Reviewing {filename}...")
    # simple checks: existence, non-empty, TODO comments, long lines
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        if not any(l.strip() for l in lines):
            print("⚠️ File is empty")
            sys.exit(0)
        issues = []
        for idx, line in enumerate(lines, start=1):
            if "TODO" in line or "FIXME" in line:
                issues.append(f"Line {idx}: contains TODO/FIXME")
            if len(line) > 120:
                issues.append(f"Line {idx}: line exceeds 120 characters")
        if issues:
            print("🔍 Findings:")
            for issue in issues:
                print(f" - {issue}")
        else:
            print("✅ No obvious issues found. Good job!")
    except Exception as e:
        print(f"Error reading file: {e}")
