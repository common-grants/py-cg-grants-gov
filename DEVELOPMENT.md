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
| `feat:`| A new feature| 
| `fix:` | A bug fix |
| `docs:` | Documentation only changes |
| `refactor:` | Code restructuring with no behavior change |

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

2. **Wait for the release workflow** (`CD - Create Release`) to run automatically on push to `main`. This kicks off two jobs:
   - **`release-please`** — opens or updates a release PR that bumps the version in `pyproject.toml` and updates `CHANGELOG.md`. If the PR already exists, it appends any new commits to it. If a release PR was previously merged, this step creates a new GitHub release and tag.
   - **`publish`** — runs only when `release-please` creates a new release. It calls the `CD - Publish to PyPI` workflow, which builds the package with `poetry build` and publishes it to PyPI using trusted publishing (OIDC — no API token required).

   You can also trigger the publish step manually by navigating to **Actions → CD - Publish to PyPI → Run workflow** and providing the tag to publish.

3. **Merge the release PR** when you're ready to cut the release. This is the only manual step — merging the PR is what triggers the actual GitHub release and the subsequent PyPI publish on the next workflow run.

### Retrying a failed publish

If the publish step fails after a release is created:

1. Go to **Actions → CD - Publish to PyPI**
2. Click **Run workflow**
3. Enter the git tag (e.g., `v0.2.0`)
4. Click **Run workflow**

If the failure requires a code fix (not just a CI retry):

1. **Revert the release PR** — create a revert PR that undoes the version bump and changelog changes from the failed release. This ensures `main` reflects the unpublished state.

   ```bash
   # Find the merge commit of the release PR
   git log --oneline main

   # Create a revert branch
   git checkout -b revert-release-v0.2.0 main
   git revert --no-edit <merge-commit-sha>
   git push -u origin revert-release-v0.2.0
   ```

2. **Merge the revert PR** to `main`.
3. **Delete the unpublished GitHub Release and tag** — go to the repo's Releases page, delete the `v0.2.0` release, then delete the tag:

   ```bash
   git push origin --delete v0.2.0
   ```

4. **Merge your fix PR** to `main`.
5. **Release-please will open a new release PR** for `v0.2.0` (same version, since the revert undid the previous bump) that includes both the original changes and your fix.
6. **Merge the new release PR** to publish.

### Previewing a release

The release PR is the primary way to preview a release — it shows the exact changelog, version bump, and all included commits.

### Bundling multiple changes

The release PR accumulates all version-bumping commits since the last release. Keep merging PRs to `main` — the release PR updates automatically. Merge the release PR only when you're ready to cut a release.

### Repository setup

These settings are required for the release workflow to function correctly:

- **Squash merge**: Enable squash merging as the default merge strategy with "Default to pull request title" so PR titles become the conventional commit messages on `main`
- **GitHub Environment**: Create an environment called `pypi` with required reviewers to add an approval gate before publishing. This environment is already referenced in the `cd-publish.yml` workflow.

### Changelog

`CHANGELOG.md` is auto-generated and updated by Release Please. Do not edit it manually.
