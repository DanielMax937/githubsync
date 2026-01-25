#!/bin/bash
# Convenience script for running cookbook services with uv

case "$1" in
  clone-repos)
    uv run python clone_github.py
    ;;
  update-repos)
    uv run python update_repos.py
    ;;
  test-oneapi)
    uv run python oneapi.py
    ;;
  test-volc)
    uv run python vol_test.py
    ;;
  test-gemini)
    uv run python browser.py
    ;;
  *)
    echo "Usage: $0 {clone-repos|update-repos|test-oneapi|test-volc|test-gemini}"
    echo ""
    echo "Available commands:"
    echo "  clone-repos    - Clone starred and trending GitHub repositories"
    echo "  update-repos   - Update all local Git repositories"
    echo "  test-oneapi    - Test OneAPI service"
    echo "  test-volc      - Test Volcengine ARK API"
    echo "  test-gemini    - Test Google Gemini API"
    exit 1
    ;;
esac
