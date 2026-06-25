"""Grants.gov CommonGrants plugin.

Maps GET /v1/opportunities/:id (OpportunityWithAttachmentsV1Schema)
to and from the CommonGrants OpportunityBase format.
"""

from __future__ import annotations

from common_grants_sdk import PluginSchemas, define_plugin, schema
from common_grants_sdk.extensions import PluginMeta
from common_grants_sdk.schemas.pydantic.models import OpportunityBase

from .models import GrantsGovOpportunitySchema, OpportunityFields
from .transforms import from_common, to_common

grants_gov = define_plugin(
    PluginSchemas(
        Opportunity=schema(
            source_schema=GrantsGovOpportunitySchema,
            common_schema=OpportunityBase[OpportunityFields],
            to_common=to_common,
            from_common=from_common,
        )
    ),
    meta=PluginMeta(
        name="grants.gov",
        source_system="Simpler.Grants.gov",
        capabilities=["customFields", "transforms"],
    ),
)

__all__ = ["grants_gov"]
