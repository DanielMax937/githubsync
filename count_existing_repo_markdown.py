import os
from pathlib import Path


REPO_BASE_DIR = Path("/Volumes/SE/git")


def main() -> None:
    if not REPO_BASE_DIR.exists():
        raise SystemExit(f"Repo base dir not found: {REPO_BASE_DIR}")

    total_repos = 0
    total_md_files = 0

    for repo_path in REPO_BASE_DIR.iterdir():
        if not repo_path.is_dir():
            continue
        if not (repo_path / ".git").exists():
            continue
        md_count = 0
        for root, dirs, files in os.walk(repo_path, topdown=True, followlinks=False):
            dirs[:] = [d for d in dirs if d != ".git"]
            for filename in files:
                if filename.lower().endswith(".md"):
                    md_count += 1
        total_repos += 1
        total_md_files += md_count

    print(f"repos={total_repos}")
    print(f"markdown_files={total_md_files}")


if __name__ == "__main__":
    main()
