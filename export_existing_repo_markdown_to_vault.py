import os
from pathlib import Path


REPO_BASE_DIR = "/Volumes/SE/git"
VAULT_RAW_DIR = "/Users/caoxiaopeng/Desktop/GitHub 知识库/00_Raw"


def infer_repo_url(repo_path: Path) -> str:
    git_config = repo_path / ".git" / "config"
    if not git_config.exists():
        return ""
    text = git_config.read_text(encoding="utf-8", errors="ignore")
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("url = "):
            continue
        raw = stripped.split("=", 1)[1].strip()
        if raw.startswith("git@github.com:"):
            path = raw.replace("git@github.com:", "").removesuffix(".git")
            return f"https://github.com/{path}"
        if raw.startswith("https://github.com/"):
            return raw.removesuffix(".git")
    return ""


def export_repo_markdown(repo_path: Path) -> int:
    repo_name = repo_path.name
    repo_url = infer_repo_url(repo_path)
    copied = 0
    for md_file in repo_path.rglob("*.md"):
        # skip markdown files inside .git internals if any
        if ".git" in md_file.parts:
            continue
        rel_path = md_file.relative_to(repo_path)
        safe_rel = str(rel_path).replace(os.sep, "__")
        target_name = f"{repo_name}__{safe_rel}"
        target_path = Path(VAULT_RAW_DIR) / target_name

        try:
            content = md_file.read_text(encoding="utf-8", errors="ignore")
            if content and not content.endswith("\n"):
                content += "\n"
            if repo_url:
                content += f"github url: {repo_url}\n"
            else:
                content += "github url: \n"
            target_path.write_text(content, encoding="utf-8")
            copied += 1
        except Exception as exc:
            print(f"⚠️ Failed: {md_file} ({exc})")
    return copied


def main() -> None:
    base = Path(REPO_BASE_DIR)
    raw_dir = Path(VAULT_RAW_DIR)
    if not base.exists():
        raise SystemExit(f"Repo base dir not found: {base}")
    raw_dir.mkdir(parents=True, exist_ok=True)

    total_files = 0
    total_repos = 0
    for repo_path in base.iterdir():
        if not repo_path.is_dir():
            continue
        if not (repo_path / ".git").exists():
            continue
        copied = export_repo_markdown(repo_path)
        total_repos += 1
        total_files += copied
        print(f"📚 {repo_path.name}: copied {copied} markdown files")

    print(f"\n✅ Done. repos={total_repos}, markdown_files={total_files}, target={raw_dir}")


if __name__ == "__main__":
    main()
