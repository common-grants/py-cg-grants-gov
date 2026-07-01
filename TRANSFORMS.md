# Transforms reference

This document covers the transform system for the `cg-grants-gov` plugin: how `to_common` and `from_common` work, what every custom field represents, the status and applicant-type mappings, and a step-by-step guide for writing your own plugin modelled on this one.

## Table of contents <!-- omit in toc -->

- [Transform contract](#transform-contract)
  - [Function signatures](#function-signatures)
  - [TransformResult](#transformresult)
  - [Error handling](#error-handling)
- [Field mapping: grants.gov → CommonGrants](#field-mapping-grantsgov--commongrants)
- [Custom fields reference](#custom-fields-reference)
  - [Scalar fields](#scalar-fields)
  - [Object fields](#object-fields)
  - [Array fields](#array-fields)
- [Status mapping](#status-mapping)
- [Applicant-type mapping](#applicant-type-mapping)
- [Wire format notes](#wire-format-notes)
- [Writing your own plugin](#writing-your-own-plugin)
  - [1. Define a source schema](#1-define-a-source-schema)
  - [2. Declare custom fields](#2-declare-custom-fields)
  - [3. Write transforms](#3-write-transforms)
  - [4. Assemble the plugin](#4-assemble-the-plugin)

---

## Transform contract

### Function signatures

```python
def to_common(
    native: GrantsGovOpportunitySchema | dict,
) -> TransformResult[OpportunityBase[OpportunityFields]]: ...

def from_common(
    common: OpportunityBase[OpportunityFields] | dict,
) -> TransformResult[GrantsGovOpportunitySchema]: ...
```

Both functions accept either a validated Pydantic model or a raw `dict`. When given a `dict`, they call `model_validate()` on the appropriate schema before transforming.

### TransformResult

Both functions return a `TransformResult[T]` — never a bare value, never an exception:

```python
@dataclass
class TransformResult(Generic[T]):
    result: T                   # The transformed value; may be partial if errors occurred
    errors: list[TransformError]  # Empty on success
```

A `TransformError` carries structured context:

```python
class TransformError(Exception):
    message: str         # Human-readable description
    path: str | None     # Dot-notation path to the failing field (e.g. "summary.fiscal_year")
    handler: str | None  # Name of the handler that raised the error
    source_value: Any    # The full input record (may contain PII — handle carefully)
    cause: Exception | None  # The original exception
```

### Error handling

Always check `result.errors` before using `result.result`:

```python
result = to_common(source_data)

if result.errors:
    for err in result.errors:
        print(f"[{err.path}] {err.message}")
        if err.cause:
            print(f"  caused by: {err.cause}")
else:
    opp = result.result
    # use opp safely
```

`result.result` is always populated (even on partial failure), but it may be incomplete when errors are present. Do not use it without checking errors first unless you intentionally want partial data.

> [!WARNING]
> `TransformError.source_value` contains the full source record and is not redacted by the SDK. Treat it as potentially sensitive and avoid logging it in production without scrubbing PII fields.

---

## Field mapping: grants.gov → CommonGrants

The table below shows how top-level fields from `GrantsGovOpportunitySchema` (and its nested `OpportunitySummarySource`) are mapped to `OpportunityBase` fields.

| Source field | CommonGrants field | Notes |
|---|---|---|
| `opportunity_id` | `id` | UUID, stringified |
| `opportunity_title` | `title` | Falls back to `""` if absent |
| `summary.summary_description` | `description` | Falls back to `""` if absent |
| `opportunity_status` | `status.value` | See [Status mapping](#status-mapping) |
| `created_at` | `createdAt` | Top-level opportunity timestamp |
| `updated_at` | `lastModifiedAt` | Top-level opportunity timestamp |
| `summary.estimated_total_program_funding` | `funding.totalAmountAvailable` | Integer cents → `{amount, currency: "USD"}` |
| `summary.award_floor` | `funding.minAwardAmount` | Integer cents → `{amount, currency: "USD"}` |
| `summary.award_ceiling` | `funding.maxAwardAmount` | Integer cents → `{amount, currency: "USD"}` |
| `summary.expected_number_of_awards` | `funding.estimatedAwardCount` | Integer |
| `summary.post_date` | `keyDates.postDate` | `SingleDateEvent` |
| `summary.close_date` | `keyDates.closeDate` | `SingleDateEvent`; description from `close_date_description` |
| `summary.archive_date` | `keyDates.otherDates.archiveDate` | `SingleDateEvent` |
| `summary.forecasted_post_date` | `keyDates.otherDates.forecastedPostDate` | `SingleDateEvent` |
| `summary.forecasted_close_date` | `keyDates.otherDates.forecastedCloseDate` | `SingleDateEvent`; description from `forecasted_close_date_description` |
| `summary.forecasted_award_date` | `keyDates.otherDates.forecastedAwardDate` | `SingleDateEvent` |
| `summary.forecasted_project_start_date` | `keyDates.otherDates.forecastedProjectStartDate` | `SingleDateEvent` |
| `summary.applicant_types` | `acceptedApplicantTypes` | See [Applicant-type mapping](#applicant-type-mapping) |

All remaining source fields are carried forward as custom fields. See the [Custom fields reference](#custom-fields-reference) below.

---

## Custom fields reference

Custom fields are declared in `OpportunityFields` (a `CustomFieldSet` subclass in `models.py`). They are present on `opp.custom_fields` after parsing or transforming.

Python attribute names are snake_case; wire names are camelCase (auto-derived by `CustomFieldSet`'s alias generator).

### Scalar fields

| Python attribute | Wire name | Type | Source field | Description |
|---|---|---|---|---|
| `legacy_serial_id` | `legacySerialId` | `int` | `legacy_opportunity_id` | Integer ID for legacy system compatibility |
| `legacy_agency_code` | `legacyAgencyCode` | `str` | `agency` | Deprecated top-level agency code string |
| `federal_opportunity_number` | `federalOpportunityNumber` | `str` | `opportunity_number` | Federal opportunity number |
| `federal_funding_source` | `federalFundingSource` | `str` | `category` | Funding category type code |
| `fiscal_year` | `fiscalYear` | `int` | `summary.fiscal_year` | Fiscal year for the opportunity |
| `funding_category_description` | `fundingCategoryDescription` | `str` | `summary.funding_category_description` | Free-text description of the funding category |
| `applicant_eligibility_description` | `applicantEligibilityDescription` | `str` | `summary.applicant_eligibility_description` | Free-text description of eligible applicants |
| `version_number` | `versionNumber` | `int` | `summary.version_number` | Opportunity summary version number |
| `category_explanation` | `categoryExplanation` | `str` | `category_explanation` | Explanation when category is "other" |
| `agency_email_address_description` | `agencyEmailAddressDescription` | `str` | `summary.agency_email_address_description` | Link text for the agency email address |
| `summary_created_at` | `summaryCreatedAt` | `str` | `summary.created_at` | ISO 8601 timestamp when the opportunity summary was created |
| `summary_updated_at` | `summaryUpdatedAt` | `str` | `summary.updated_at` | ISO 8601 timestamp when the opportunity summary was last updated |

> **Why separate summary timestamps?** `summary.created_at` / `summary.updated_at` track when the summary record changed, independently of the top-level opportunity timestamps. Both are preserved as custom fields so a `from_common` round-trip can reconstruct them accurately.

### Object fields

| Python attribute | Wire name | Value type | Description |
|---|---|---|---|
| `agency` | `agency` | `AgencyValue` | Agency code, name, parent name, parent code |
| `contact_info` | `contactInfo` | `ContactInfoValue` | Agency contact email and description |
| `additional_info` | `additionalInfo` | `AdditionalInfoValue` | URL and description for additional info |
| `cost_sharing` | `costSharing` | `CostSharingValue` | Whether cost sharing is required |

**AgencyValue**

```python
class AgencyValue(BaseModel):
    code: Optional[str]        # e.g. "HHS-ACF"   (source: agency_code)
    name: Optional[str]        # e.g. "Administration for Children and Families"
    parentName: Optional[str]  # e.g. "Department of Health and Human Services"
    parentCode: Optional[str]  # e.g. "HHS"
```

**ContactInfoValue**

```python
class ContactInfoValue(BaseModel):
    name: Optional[str]         # Contact name (not in v1 source; always None)
    email: Optional[str]        # source: summary.agency_email_address
    phone: Optional[str]        # Not in v1 source; always None
    description: Optional[str]  # source: summary.agency_contact_description
```

**AdditionalInfoValue**

```python
class AdditionalInfoValue(BaseModel):
    url: Optional[str]          # source: summary.additional_info_url
    description: Optional[str]  # source: summary.additional_info_url_description
```

**CostSharingValue**

```python
class CostSharingValue(BaseModel):
    isRequired: Optional[bool]  # source: summary.is_cost_sharing
```

### Array fields

| Python attribute | Wire name | Element type | Description |
|---|---|---|---|
| `assistance_listings` | `assistanceListings` | `AssistanceListingValue` | Assistance listing numbers and program titles |
| `attachments` | `attachments` | `AttachmentValue` | NOFOs and supplemental documents |
| `funding_instruments` | `fundingInstruments` | `str` | Funding instrument type strings |
| `funding_categories` | `fundingCategories` | `str` | Funding category type strings |
| `competitions` | `competitions` | `CompetitionValue` | Competitions associated with the opportunity |

**AssistanceListingValue**

```python
class AssistanceListingValue(BaseModel):
    identifier: Optional[str]    # source: assistance_listing_number  e.g. "93.123"
    programTitle: Optional[str]  # source: program_title
```

**AttachmentValue**

```python
class AttachmentValue(BaseModel):
    opportunityAttachmentId: Optional[UUID]
    downloadUrl: Optional[str]   # source: download_path
    name: str                    # source: file_name
    description: Optional[str]  # source: file_description
    sizeInBytes: Optional[int]  # source: file_size_bytes
    mimeType: Optional[str]
    createdAt: datetime          # source: attachment.created_at, falls back to opportunity.created_at
    lastModifiedAt: datetime     # source: attachment.updated_at, falls back to opportunity.updated_at
```

**CompetitionValue**

```python
class CompetitionValue(BaseModel):
    competitionId: UUID
    opportunityId: UUID
    competitionTitle: Optional[str]
```

---

## Status mapping

**`to_common`** (Grants.gov → CommonGrants):

| `opportunity_status` | `status.value` |
|---|---|
| `forecasted` | `forecasted` |
| `posted` | `open` |
| `closed` | `closed` |
| `archived` | `closed` |

**`from_common`** (CommonGrants → Grants.gov):

| `status.value` | `opportunity_status` |
|---|---|
| `forecasted` | `forecasted` |
| `open` | `posted` |
| `closed` | `closed` |
| `custom` | `posted` (default fallback) |

The `is_forecast` field on `OpportunitySummarySource` is derived from the status: it is `True` when `opportunity_status == "forecasted"`.

---

## Applicant-type mapping

**`to_common`** (Grants.gov → CommonGrants):

| `applicant_types` value | CommonGrants `value` |
|---|---|
| `state_governments` | `government_state` |
| `county_governments` | `government_county` |
| `city_or_township_governments` | `government_municipal` |
| `special_district_governments` | `government_special_district` |
| `independent_school_districts` | `school_district_independent` |
| `public_and_state_institutions_of_higher_education` | `higher_education_public` |
| `private_institutions_of_higher_education` | `higher_education_private` |
| `federally_recognized_native_american_tribal_governments` | `government_tribal` |
| `other_native_american_tribal_organizations` | `organization_tribal_other` |
| `nonprofits_non_higher_education_with_501c3` | `non_profit_with_501c3` |
| `nonprofits_non_higher_education_without_501c3` | `nonprofit_without_501c3` |
| `individuals` | `individual` |
| `for_profit_organizations_other_than_small_businesses` | `for_profit_not_small_business` |
| `small_businesses` | `for_profit_small_business` |
| `unrestricted` | `unrestricted` |
| _(anything else)_ | `custom` (with `custom_value` set to the original string) |

**`from_common`** (CommonGrants → Grants.gov): the reverse of the table above. `"organization"` and `"custom"` both map to `"other"`.

---

## Wire format notes

Custom fields are transmitted as a `customFields` object on the wire. Each entry follows this shape:

```json
{
  "customFields": {
    "fiscalYear": {
      "name": "fiscalYear",
      "fieldType": "integer",
      "value": 2025
    },
    "agency": {
      "name": "agency",
      "fieldType": "object",
      "value": {
        "code": "HHS",
        "name": "Department of Health and Human Services",
        "parentName": null,
        "parentCode": null
      }
    }
  }
}
```

- Wire names are **camelCase** (`fiscalYear`, `agencyEmailAddressDescription`). Python attribute names are **snake_case** (`fiscal_year`, `agency_email_address_description`). The alias generator on `CustomFieldSet` handles this automatically — do not add explicit `alias=` parameters to fields.
- Value object field names inside custom fields (e.g. `AgencyValue.parentName`) are **also camelCase** by design. These are wire-format objects and deliberately not snake_case.
- `fieldType` must be one of: `"string"`, `"number"`, `"integer"`, `"boolean"`, `"object"`, `"array"`.
- Optional custom fields are omitted entirely from the payload when they have no value (absent ≠ `null`).

---

## Writing your own plugin

This section walks through creating a plugin from scratch using the same pattern as `cg-grants-gov`. For the full SDK reference see the [CommonGrants SDK extensions guide](https://github.com/HHS/simpler-grants-protocol/tree/main/lib/python-sdk/common_grants_sdk/extensions).

### 1. Define a source schema

Create a Pydantic model for your source system's data shape:

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class MySourceOpportunity(BaseModel):
    id: UUID
    title: Optional[str] = None
    status: str                 # e.g. "open" | "closed"
    description: Optional[str] = None
    max_award: Optional[int] = None
    created_at: datetime
    updated_at: datetime
```

If your source schema is not yet stable, you can use `PassthroughModel` from the SDK instead:

```python
from common_grants_sdk.extensions import PassthroughModel
# PassthroughModel accepts any extra fields — good for prototyping
```

### 2. Declare custom fields

Subclass `CustomFieldSet` and declare one `Optional[CustomField[V]]` per field you want to carry forward. The type parameter `V` determines the wire `fieldType` automatically.

```python
from typing import Optional
from pydantic import Field
from common_grants_sdk.extensions import CustomField, CustomFieldSet

class MyOpportunityFields(CustomFieldSet):
    max_award: Optional[CustomField[int]] = Field(
        default=None, description="Maximum award amount in USD"
    )
    program_code: Optional[CustomField[str]] = Field(
        default=None, description="Internal program identifier"
    )
    # For complex values, define a value schema and use it as V:
    # contact: Optional[CustomField[ContactValue]] = Field(default=None, ...)
```

Rules:
- Always `Optional[CustomField[V]] = Field(default=None, ...)`.
- Use snake_case names — `CustomFieldSet` generates camelCase wire names automatically.
- Do not add `alias=` parameters.
- For object values, define a plain `BaseModel` subclass and use it as `V`.

### 3. Write transforms

Each transform function takes the source model (or a dict) and returns a `TransformResult`.

Use `validate_into` from the SDK to validate and wrap the result in one call:

```python
from common_grants_sdk.extensions import TransformResult, validate_into
from common_grants_sdk.schemas.pydantic.models import OpportunityBase

def my_to_common(
    source: MySourceOpportunity | dict,
) -> TransformResult[OpportunityBase[MyOpportunityFields]]:
    if isinstance(source, dict):
        source = MySourceOpportunity.model_validate(source)

    # Build the customFields payload as a dict of wire-format dicts
    custom_fields = {}
    if source.max_award is not None:
        custom_fields["maxAward"] = {
            "name": "maxAward",
            "fieldType": "integer",
            "value": source.max_award,
        }
    if source.program_code is not None:
        custom_fields["programCode"] = {
            "name": "programCode",
            "fieldType": "string",
            "value": source.program_code,
        }

    payload = {
        "id": str(source.id),
        "title": source.title or "",
        "description": source.description or "",
        "status": {"value": source.status},   # map to CommonGrants status values
        "createdAt": source.created_at.isoformat(),
        "lastModifiedAt": source.updated_at.isoformat(),
        "customFields": custom_fields,
    }

    return validate_into(OpportunityBase[MyOpportunityFields], payload)


def my_from_common(
    common: OpportunityBase[MyOpportunityFields] | dict,
) -> TransformResult[MySourceOpportunity]:
    if isinstance(common, dict):
        common = OpportunityBase[MyOpportunityFields].model_validate(common)

    cf = common.custom_fields
    payload = {
        "id": str(common.id),
        "title": common.title,
        "status": common.status.value,
        "description": common.description,
        "max_award": cf.max_award.value if cf and cf.max_award else None,
        "program_code": cf.program_code.value if cf and cf.program_code else None,
        "created_at": common.created_at.isoformat(),
        "updated_at": common.last_modified_at.isoformat(),
    }

    return validate_into(MySourceOpportunity, payload)
```

`validate_into(Model, payload)` calls `Model.model_validate(payload)` and returns a `TransformResult` with any validation errors collected into `result.errors`.

### 4. Assemble the plugin

Wire the four components together with `define_plugin`:

```python
from common_grants_sdk import PluginSchemas, define_plugin, schema
from common_grants_sdk.extensions import PluginMeta
from common_grants_sdk.schemas.pydantic.models import OpportunityBase

my_plugin = define_plugin(
    PluginSchemas(
        Opportunity=schema(
            source_schema=MySourceOpportunity,
            common_schema=OpportunityBase[MyOpportunityFields],
            to_common=my_to_common,
            from_common=my_from_common,
        )
    ),
    meta=PluginMeta(
        name="my-system",
        source_system="My Grant System",
        capabilities=["customFields", "transforms"],
    ),
)
```

Consumers then use the plugin as:

```python
# Parse a CommonGrants-format dict
opp = my_plugin.schemas.Opportunity.model_validate(api_response)

# Transform from source format
result = my_plugin.schemas.Opportunity.to_common(source_data)
if not result.errors:
    print(result.result.custom_fields.max_award.value)

# Transform back to source format
result = my_plugin.schemas.Opportunity.from_common(opp)
```

`define_plugin` validates the plugin at import time and raises `PluginDefinitionError` if the schema wiring is invalid (e.g. a schema name doesn't match a registered extensible schema).
