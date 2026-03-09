
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python review.py <file_to_review>")
        sys.exit(1)
    filename = sys.argv[1]
    print(f"Reviewing {filename}...")
    # simple check: file must exist and not be empty
    try:
        with open(filename, 'r') as f:
            content = f.read()
        if not content.strip():
            print("⚠️ File is empty")
        else:
            print("✅ Looks good!")
    except Exception as e:
        print(f"Error reading file: {e}")
