# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Python-based toolkit for GitHub repository management and AI API testing. The codebase consists of standalone scripts that automate GitHub operations and test various AI service providers.

**Key files:**
- `run.sh` - Convenience wrapper script for running services with uv
- `pyproject.toml` - Modern Python project configuration and dependencies
- `requirments.txt` - Legacy requirements file (kept for compatibility)
- `clone_github.py` - Clone starred and trending GitHub repos
- `update_repos.py` - Update all local Git repositories
- `oneapi.py`, `vol_test.py`, `browser.py` - AI API testing scripts

## Environment Setup

All scripts require environment variables stored in `.env`:
- `GOOGLE_API_KEY` - For Google Gemini API access
- `GITHUP_TOKEN` - GitHub personal access token for API operations
- `ONE_API_KEY` and `BASE_URL` - For OneAPI service
- `ARK_API_KEY` - For Volcengine ARK API

Install dependencies using uv:
```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Use uv run (automatically manages environment and dependencies)
uv run python <script>.py
```

The project uses `pyproject.toml` for dependency management. The first `uv run` command will automatically create a virtual environment and install all dependencies. Legacy `requirments.txt` is kept for compatibility.

## Core Scripts

### GitHub Repository Management

**clone_github.py** - Clones starred and trending GitHub repositories
- Fetches user's starred repos via GitHub API (paginated, 1500 per page)
- Scrapes trending repos from github.com/trending
- Clones repos to `/Volumes/SE/git` using SSH (git@github.com)
- Uses ThreadPoolExecutor with 4 workers for parallel cloning
- Skips existing repos automatically
- Limits to 30 new starred repos per run

Run:
```bash
python clone_github.py
```

**update_repos.py** - Updates all local Git repositories
- Iterates through all subdirectories in `/Volumes/SE/git`
- Cleans `._*` files from `.git` directories (macOS metadata)
- Executes `git pull` on each repository
- Logs failures to `failed_repos.log` with timestamps

Run:
```bash
python update_repos.py
```

### AI API Testing Scripts

**browser.py** - Minimal Google Gemini client initialization
- Sets up `genai.Client` with API key from environment

**oneapi.py** - Tests OneAPI service (OpenAI-compatible interface)
- Configures OpenAI client to point to custom base URL
- Tests chat completions with `gemini-2.5-flash-preview-04-17` model
- Demonstrates error handling for API calls

**vol_test.py** - Tests Volcengine ARK API
- Uses OpenAI SDK with custom base URL (`https://ark.cn-beijing.volces.com/api/v3`)
- Tests both streaming and non-streaming completions
- Model endpoint: `ep-20250218192809-jvz67`

Run any test script:
```bash
# With uv (automatically manages environment)
uv run python oneapi.py
uv run python vol_test.py
uv run python browser.py
```

## Architecture Notes

### GitHub Operations
- All GitHub cloning uses SSH URLs (`git@github.com:user/repo.git`) converted from HTTPS URLs
- Base directory `/Volumes/SE/git` is hardcoded - this is an external volume mount
- GitHub API uses v3 with `2022-11-28` API version header
- Trending repos are scraped via BeautifulSoup (no official API)

### API Client Pattern
All AI testing scripts follow the same pattern:
1. Load environment variables with `python-dotenv`
2. Initialize client with custom base URL (except Google's native SDK)
3. Use OpenAI SDK interface for compatibility (OneAPI, ARK)

### Concurrency
- `clone_github.py` uses ThreadPoolExecutor for parallel cloning (4 workers)
- `update_repos.py` runs sequentially to avoid git conflicts

## Common Tasks

### Using the convenience script (recommended)

```bash
# Clone new repos
./run.sh clone-repos

# Update existing repos
./run.sh update-repos

# Test AI APIs
./run.sh test-gemini      # Google Gemini
./run.sh test-oneapi      # OneAPI service
./run.sh test-volc        # Volcengine ARK
```

### Direct execution with uv

```bash
# Clone new repos
uv run python clone_github.py

# Update existing repos
uv run python update_repos.py

# Test AI APIs
uv run python browser.py      # Google Gemini
uv run python oneapi.py       # OneAPI service
uv run python vol_test.py     # Volcengine ARK
```

## Important Constraints

- GitHub token must have `repo` and `user` scopes for starred repos access
- External volume `/Volumes/SE/git` must be mounted before running GitHub scripts
- All scripts assume macOS environment (uses `find` with macOS-specific flags)
- No test suite or linting configuration present
