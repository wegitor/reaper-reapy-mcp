# Contributing

Thanks for your interest in contributing to reaper-reapy-mcp! Small, clear steps make it easy for people to help — below are the essentials to get contributors started.

1) Code of conduct

- TODO: Add CODE_OF_CONDUCT.md to the repository. Once added, link it here.

2) Getting started

- Fork the repo and create a feature branch:
  - git checkout -b feature/<my-change-name>

3) Check it
- Example using uv runner:
  - uv --directory . run -m pytest tests/mcp_client/pytest
- Or run pytest directly:
  - python -m pytest tests/mcp_client/pytest

4) Issues

- Search existing issues before opening a new one.
- For bugs, include: steps to reproduce, expected vs actual behavior, environment (OS, Python version, REAPER version), and a minimal repro if possible.

5) Pull requests

- Base branch: the repository default branch.
- Open a PR from a topic branch (not from main/default).

PR checklist (please include as a short checklist in your PR description):
- [ ] Tests added or updated (if applicable)
- [ ] Documentation updated (if applicable)
- [ ] All linters/formatters run (e.g., black, isort)

If your change is large or architectural, open an issue first to discuss design.

Thanks — maintainers will help you iterate on the PR.
