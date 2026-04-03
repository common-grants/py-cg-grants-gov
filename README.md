# cg-extension-framework

A [CommonGrants SDK](https://github.com/HHS/simpler-grants-gov) plugin that extends the `Opportunity` model with custom fields for HHS/grants.gov opportunity data.

## Overview

This plugin registers grants.gov-specific fields on the CommonGrants `Opportunity` schema, enabling consumers of the CommonGrants SDK to work with the full set of grants.gov data attributes alongside the standard CommonGrants fields.

**Custom fields added to `Opportunity`:**

| Field | Type | Description |
|---|---|---|
| `legacySerialId` | integer | Integer ID for compatibility with legacy systems |
| `federalOpportunityNumber` | string | Federal opportunity number assigned to the grant |
| `assistanceListings` | array | Assistance listing numbers and program titles |
| `agency` | object | Agency offering the opportunity |
| `attachments` | array | NOFOs and supplemental documents |
| `federalFundingSource` | string | Category type of the grant opportunity |
| `contactInfo` | object | Contact name, email, phone, and description |
| `additionalInfo` | object | URL and description for additional information |
| `fiscalYear` | integer | Fiscal year associated with the opportunity |
| `costSharing` | object | Cost sharing or matching fund requirements |

## Installation

```bash
pip install cg-extension-framework
```

Or with Poetry:

```bash
poetry add cg-extension-framework
```

## Usage

The plugin is auto-discovered by the CommonGrants SDK via its entry point. No manual registration is needed once the package is installed.

```python
from common_grants_sdk import load_plugins

# Load all installed plugins, including this one
plugins = load_plugins()
```

To use the plugin directly:

```python
from plugin import custom_fields

# Access the plugin's extensions and schemas
extensions = custom_fields.extensions
schemas = custom_fields.schemas
```

## Development

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/)

### Setup

```bash
# Clone the repository
git clone https://github.com/HHS/py-cg-grants-gov.git
cd py-cg-grants-gov

# Install dependencies
make install
```

### Commands

```bash
make install       # Install dependencies
make build         # Build the package
make checks        # Run lint, format, and type checks
make test          # Run tests
make clean         # Remove build artifacts
```

### Code quality

This project uses:
- **Black** for code formatting
- **Ruff** for linting
- **Mypy** for static type checking

Run all checks before submitting a pull request:

```bash
make checks
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is in the public domain. See [LICENSE.md](LICENSE.md) for details.
