# Contributing

Thank you for your interest in contributing. Contributions are welcome.

## Getting started

1. Fork the repository and clone it locally.
2. Install dependencies: `make install`
3. Create a branch for your change: `git checkout -b your-branch-name`

## Making changes

- Keep changes focused. One logical change per pull request.
- Run `make checks` before pushing — CI enforces formatting, linting, and type checks.
- Add or update tests for any behavior you change. Run `make test` to verify.

## Pull request guidelines

- Use a [Conventional Commits](https://www.conventionalcommits.org/) prefix in your PR title (e.g., `feat:`, `fix:`, `chore:`). This is enforced by CI and drives automated versioning.
- Describe what your change does and why in the PR description.
- Link any related issues.

## Reporting issues

Open a GitHub issue with a clear description of the problem, steps to reproduce it, and the expected versus actual behavior.
