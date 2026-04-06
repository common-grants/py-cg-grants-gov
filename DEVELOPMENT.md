# Development

## Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)

## Setup

```bash
# Clone the repository
git clone https://github.com/HHS/py-cg-grants-gov.git
cd py-cg-grants-gov

# Install dependencies
make install
```

## Commands

```bash
make install       # Install dependencies
make build         # Build the package
make checks        # Run lint, format, and type checks
make test          # Run tests
make clean         # Remove build artifacts
```

## Code quality

This project uses:
- **Black** for code formatting
- **Ruff** for linting
- **Mypy** for static type checking

Run all checks before submitting a pull request:

```bash
make checks
```

## Releases and versioning

This project uses [Release Please](https://github.com/googleapis/release-please) to automate versioning and changelog generation, and publishes to [PyPI](https://pypi.org/p/cg-grants-gov) via a manually triggered GitHub Actions workflow.

### How versioning works

Versions follow [Semantic Versioning](https://semver.org/) (`MAJOR.MINOR.PATCH`) and are driven entirely by [conventional commit](https://www.conventionalcommits.org/) messages merged into `main`. Commits that don't follow the conventional commit format are ignored by Release Please and won't contribute to a version bump.

#### Patch (`0.1.0` → `0.1.1`)

Backwards-compatible bug fixes and non-functional changes:

| Prefix | Use for |
|---|---|
| `fix:` | A bug fix |
| `perf:` | A performance improvement with no API change |
| `refactor:` | Code restructuring with no behavior change |
| `docs:` | Documentation only changes |
| `chore:` | Maintenance tasks (dependency updates, build config, etc.) |
| `style:` | Formatting, whitespace, missing semicolons, etc. |
| `test:` | Adding or updating tests |
| `ci:` | CI/CD configuration changes |

#### Minor (`0.1.0` → `0.2.0`)

New backwards-compatible functionality:

| Prefix | Use for |
|---|---|
| `feat:` | A new feature or capability |

#### Major (`0.1.0` → `1.0.0`)

Breaking changes that are not backwards-compatible:

| Prefix | Use for |
|---|---|
| `feat!:` or `fix!:` (any type with `!`) | A breaking change |
| `BREAKING CHANGE:` in the commit footer | A breaking change (alternative syntax) |

Example of a breaking change using the footer syntax:

```
feat: rename opportunity fields

BREAKING CHANGE: `legacyId` has been renamed to `legacySerialId`
```

### Release runbook

1. **Merge changes to `main`** using conventional commit messages. Release Please tracks these commits to determine what the next version bump should be.

2. **Trigger the release workflow** by navigating to **Actions → CD - Deploy Plugin to PyPI → Run workflow** in GitHub. This kicks off two jobs:
   - **`release-please`** — opens or updates a release PR that bumps the version in `pyproject.toml` and updates `CHANGELOG.md`. If the PR already exists, it appends any new commits to it. If a release PR was previously merged, this step creates a new GitHub release and tag.
   - **`deploy`** — runs only when `release-please` creates a new release. It builds the package with `poetry build` and publishes it to PyPI using trusted publishing (OIDC — no API token required).

3. **Merge the release PR** when you're ready to cut the release. This is the only manual step — merging the PR is what triggers the actual GitHub release and the subsequent PyPI publish on the next workflow run.

### Changelog

`CHANGELOG.md` is auto-generated and updated by Release Please. Do not edit it manually.
