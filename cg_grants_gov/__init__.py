"""Grants.gov CommonGrants plugin.

Maps GET /v1/opportunities/:id (OpportunityWithAttachmentsV1Schema) to and from
the CommonGrants OpportunityBase format, and registers the custom filters the
Simpler.Grants.gov search accepts.
"""

from __future__ import annotations

from common_grants_sdk import PluginSchemas, define_plugin, schema
from common_grants_sdk.extensions import PluginMeta, PluginRoutes, ResourceRoutes
from common_grants_sdk.schemas.pydantic.filters.opportunity import (
    BooleanComparison,
    OpportunityFilters,
    StringArray,
)
from common_grants_sdk.schemas.pydantic.models import OpportunityBase

from .models import GrantsGovOpportunitySchema, OpportunityFields
from .transforms import from_common, to_common


class OppSearchFilters(OpportunityFilters, total=False):
    """Custom filters accepted on Simpler.Grants.gov opportunities.search.

    Each key's annotation is its filter value model; the SDK validates the
    call-site value against it and recovers the type when classifying the
    request body. Keys are camelCase to match the wire (customFilters) names.
    """

    agency: StringArray
    applicantType: StringArray
    fundingInstrument: StringArray
    costSharing: BooleanComparison


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

__all__ = ["OppSearchFilters", "grants_gov"]
