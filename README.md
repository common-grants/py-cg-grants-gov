# cg-grants-gov

A [CommonGrants SDK](https://github.com/HHS/simpler-grants-protocol/tree/main/lib/python-sdk) plugin that extends the `Opportunity` model with custom fields for [HHS/simpler-grants-gov](https://github.com/HHS/simpler-grants-gov/) opportunity data.

## Table of contents <!-- omit in toc -->

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
  - [Parse a CommonGrants opportunity](#parse-a-commongrants-opportunity)
  - [Search with custom filters](#search-with-custom-filters)
  - [Transform from grants.gov source format](#transform-from-grantsgov-source-format)
  - [Transform back to grants.gov format](#transform-back-to-grantsgov-format)
- [Plugin anatomy](#plugin-anatomy)
- [Development](#development)
- [Contributing](#contributing)
- [License](#license)

## Overview

This plugin registers grants.gov-specific fields on the CommonGrants `Opportunity` schema, provides bidirectional transforms between the grants.gov v1 API format (`GrantsGovOpportunitySchema`) and the CommonGrants `OpportunityBase` format, and registers the custom search filters that Simpler.Grants.gov accepts on `opportunities.search`.

**Capabilities:** `customFields`, `transforms`, `customFilters`

See [TRANSFORMS.md](TRANSFORMS.md) for the complete field mapping reference, custom fields table, status and applicant-type mappings, and a guide to writing your own plugin.

## Installation

```bash
pip install cg-grants-gov
```

Or with Poetry:

```bash
poetry add cg-grants-gov
```

## Usage

### Parse a CommonGrants opportunity

Parse an opportunity already in CommonGrants format (e.g. from the API) into the typed model, including all grants.gov custom fields:

```python
from cg_grants_gov import grants_gov

opp_raw = {
    "id": "573525f2-8e15-4405-83fb-e6523511d893",
    "title": "STEM Education Grant Program",
    "status": {"value": "open"},
    "description": "A grant program focused on STEM education.",
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

### Search with custom filters

The plugin registers four custom search filters on `opportunities.search`, in
addition to the standard CommonGrants filters:

| Filter | Family |
|---|---|
| `agency` | `StringArray` |
| `applicantType` | `StringArray` |
| `fundingInstrument` | `StringArray` |
| `costSharing` | `BooleanComparison` |

A client from `grants_gov.get_client(...)` binds these filters, so
`search(filters=...)` validates each value against its declared filter model and
raises `FilterError` fail-fast for a wrong-typed value before any request is sent:

```python
from common_grants_sdk.client import Config
from common_grants_sdk.extensions import f

from cg_grants_gov import grants_gov

client = grants_gov.get_client(
    Config(base_url="https://api.simpler.grants.gov", api_key="your-api-key"),
)

result = client.opportunities.search(
    filters={
        "status": f.in_(["open"]),
        "agency": f.in_(["NSF"]),
        "applicantType": f.in_(["state_governments"]),
        "fundingInstrument": f.in_(["grant"]),
        "costSharing": f.eq(False),
    },
    page=1,
)

print(result.pagination_info.total_items)
for opp in result.items:
    print(opp.title, opp.custom_fields.agency.value.code)
```

For a runnable end-to-end version, see
[`examples/search_with_filters.py`](examples/search_with_filters.py). It calls
the live Simpler.Grants.gov API, so it requires an `SGG_API_KEY`; `SGG_BASE_URL`
is optional and defaults to the production API. Run it with:

```bash
poetry run python examples/search_with_filters.py
```

### Transform from grants.gov source format

Convert a raw grants.gov v1 API response to CommonGrants format:

```python
from cg_grants_gov import grants_gov
from cg_grants_gov.transforms import to_common

source = {
    "opportunity_id": "573525f2-8e15-4405-83fb-e6523511d893",
    "opportunity_title": "STEM Education Grant Program",
    "opportunity_status": "posted",
    "agency_code": "HHS",
    "agency_name": "Department of Health and Human Services",
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-15T00:00:00Z",
    "summary": {
        "summary_description": "A grant program focused on STEM education.",
        "is_forecast": False,
        "fiscal_year": 2025,
        "award_ceiling": 500000,
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-15T00:00:00Z",
    },
}

result = to_common(source)

if result.errors:
    for err in result.errors:
        print(f"Transform error at {err.path}: {err.message}")
else:
    opp = result.result
    print(opp.title)                              # "STEM Education Grant Program"
    print(opp.status.value)                       # "open"  (posted → open)
    print(opp.custom_fields.fiscal_year.value)    # 2025
    print(opp.custom_fields.agency.value.code)    # "HHS"
```

### Transform back to grants.gov format

Convert a CommonGrants opportunity back to grants.gov format:

```python
from cg_grants_gov.transforms import from_common

result = from_common(opp)

if not result.errors:
    native = result.result
    print(native.opportunity_status)    # "posted"
    print(native.agency_code)           # "HHS"
    print(native.summary.fiscal_year)   # 2025
```

## Plugin anatomy

The plugin is assembled in `cg_grants_gov/__init__.py` using these components:

| Component | What it is | File |
|---|---|---|
| `GrantsGovOpportunitySchema` | Pydantic model for the grants.gov v1 API response | `models.py` |
| `OpportunityFields` | `CustomFieldSet` subclass declaring all 21 custom fields | `models.py` |
| `to_common` | Transforms `GrantsGovOpportunitySchema → OpportunityBase[OpportunityFields]` | `transforms.py` |
| `from_common` | Transforms `OpportunityBase[OpportunityFields] → GrantsGovOpportunitySchema` | `transforms.py` |
| `OppSearchFilters` | `OpportunityFilters` subclass declaring the custom search filters | `__init__.py` |

`OppSearchFilters` extends the SDK's `OpportunityFilters` with the four custom
filters documented under [Search with custom filters](#search-with-custom-filters),
each annotated with its filter family so the SDK validates call-site values and
recovers their type when classifying the request.

The schema, transforms, and filter routes are wired together via `define_plugin`.
Passing `OppSearchFilters` through `PluginRoutes` is what registers the custom
filters on `opportunities.search` and backs the `customFilters` capability:

```python
from common_grants_sdk import PluginSchemas, define_plugin, schema
from common_grants_sdk.extensions import PluginMeta, PluginRoutes, ResourceRoutes

grants_gov = define_plugin(
    PluginSchemas(
        Opportunity=schema(
            source_schema=GrantsGovOpportunitySchema,
            common_schema=OpportunityBase[OpportunityFields],
            to_common=to_common,
            from_common=from_common,
        )
    ),
    routes=PluginRoutes(opportunities=ResourceRoutes(search=OppSearchFilters)),
    meta=PluginMeta(
        name="grants.gov",
        source_system="Simpler.Grants.gov",
        capabilities=["customFields", "transforms", "customFilters"],
    ),
)
```

See [TRANSFORMS.md](TRANSFORMS.md) for a detailed walkthrough of how to write your own plugin modelled on this one.

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md) for setup instructions, available commands, and the release runbook.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is in the public domain. See [LICENSE.md](LICENSE.md) for details.
