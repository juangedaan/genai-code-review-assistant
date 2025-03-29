
import os
from github import Github
import openai

# Load secrets
openai.api_key = os.getenv("OPENAI_API_KEY")
gh = Github(os.getenv("GH_TOKEN"))

# Assume repo context comes from GitHub Actions
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = int(os.getenv("GITHUB_REF").split('/')[-1])
repo = gh.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# Fetch diff and files
diff = ""
for file in pr.get_files():
    if file.patch:
        diff += f"File: {file.filename}\n{file.patch}\n"

# Call OpenAI
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a senior code reviewer."},
        {"role": "user", "content": f"Review the following diff:\n{diff}"}
    ],
    temperature=0.3
)

# Post comment
review_text = response.choices[0].message["content"]
pr.create_issue_comment(f"🤖 GenAI Review:\n\n{review_text}")
