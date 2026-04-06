# cg-grants-gov

A [CommonGrants SDK](https://github.com/HHS/simpler-grants-gov) plugin that extends the `Opportunity` model with custom fields for HHS/grants.gov opportunity data.

## Overview

This plugin registers grants.gov-specific fields on the CommonGrants `Opportunity` schema, enabling consumers of the CommonGrants SDK to work with the full set of grants.gov data attributes alongside the standard CommonGrants fields.

## Installation

```bash
pip install cg-grants-gov
```

Or with Poetry:

```bash
poetry add cg-grants-gov
```

## Usage

The plugin is auto-discovered by the CommonGrants SDK via its entry point. No manual registration is needed once the package is installed.


To use the plugin directly:

```python
from cg_grants_gov import schemas

# Access the extended Opportunity model
Opportunity = schemas.Opportunity
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for setup instructions, available commands, and the release runbook.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is in the public domain. See [LICENSE.md](LICENSE.md) for details.
