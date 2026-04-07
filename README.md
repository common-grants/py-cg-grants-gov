# cg-grants-gov

A [CommonGrants SDK](https://github.com/HHS/simpler-grants-protocol/tree/main/lib/python-sdk) plugin that extends the `Opportunity` model with custom fields for [HHS/simpler-grants-gov](https://github.com/HHS/simpler-grants-gov/) opportunity data.

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

To parse a grants.gov opportunity using the plugin:

```python
from cg_grants_gov import grants_gov

opp_raw = {
    "id": "573525f2-8e15-4405-83fb-e6523511d893",
    "title": "STEM Education Grant Program",
    "status": {"value": "open"},
    "createdAt": "2025-01-01T00:00:00Z",
    "lastModifiedAt": "2025-01-15T00:00:00Z",
    "customFields": {
        "agency": {
            "name": "agency",
            "fieldType": "object",
            "value": {"code": "HHS", "name": "Department of Health and Human Services"},
        },
        "fiscalYear": {"name": "fiscalYear", "fieldType": "integer", "value": 2025},
    },
}

opp = grants_gov.schemas.Opportunity.model_validate(opp_raw)

print(opp.title)                              # "STEM Education Grant Program"
print(opp.custom_fields.agency.value.name)    # "Department of Health and Human Services"
print(opp.custom_fields.fiscal_year.value)    # 2025
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for setup instructions, available commands, and the release runbook.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is in the public domain. See [LICENSE.md](LICENSE.md) for details.
