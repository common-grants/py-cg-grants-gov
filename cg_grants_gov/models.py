"""Pydantic models for the Grants.gov CommonGrants plugin.

Sections:
  1. Custom field value schemas  (wire-format objects stored inside CustomField)
  2. OpportunityFields            (CustomFieldSet declaring all custom fields)
  3. Source schemas               (GrantsGovOpportunitySchema and its nested models)
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from common_grants_sdk.extensions import CustomField, CustomFieldSet

# =============================================================================
# Section 1: Custom field value schemas
# =============================================================================


class AssistanceListingValue(BaseModel):
    identifier: Optional[str] = None
    programTitle: Optional[str] = None


class AgencyValue(BaseModel):
    """Wire-format value for the agency custom field.

    Field names are camelCase Python attributes by design — this is a
    wire-format value object, not a domain model. Do NOT convert to snake_case;
    from_common accesses cf.agency.value.parentName etc. directly.
    """

    code: Optional[str] = None
    name: Optional[str] = None
    parentName: Optional[str] = None
    parentCode: Optional[str] = None


class AttachmentValue(BaseModel):
    opportunityAttachmentId: Optional[UUID] = None
    downloadUrl: Optional[str] = None
    name: str
    description: Optional[str] = None
    sizeInBytes: Optional[int] = None
    mimeType: Optional[str] = None
    createdAt: datetime
    lastModifiedAt: datetime


class ContactInfoValue(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None


class AdditionalInfoValue(BaseModel):
    url: Optional[str] = None
    description: Optional[str] = None


class CostSharingValue(BaseModel):
    isRequired: Optional[bool] = None


class CompetitionValue(BaseModel):
    competitionId: UUID
    opportunityId: UUID
    competitionTitle: Optional[str] = None


# =============================================================================
# Section 2: OpportunityFields (CustomFieldSet)
# =============================================================================


class OpportunityFields(CustomFieldSet):
    """Custom fields for grants.gov opportunities.

    snake_case Python names; camelCase wire names are auto-derived by
    CustomFieldSet's alias_generator. Do NOT add explicit alias= parameters.
    """

    legacy_serial_id: Optional[CustomField[int]] = Field(
        default=None, description="Integer ID for legacy system compatibility"
    )
    legacy_agency_code: Optional[CustomField[str]] = Field(
        default=None, description="Deprecated top-level agency code string"
    )
    federal_opportunity_number: Optional[CustomField[str]] = Field(
        default=None, description="Federal opportunity number"
    )
    assistance_listings: Optional[CustomField[list[AssistanceListingValue]]] = Field(
        default=None, description="Assistance listing number and program title"
    )
    agency: Optional[CustomField[AgencyValue]] = Field(
        default=None, description="Agency code, name, parent code, parent name"
    )
    attachments: Optional[CustomField[list[AttachmentValue]]] = Field(
        default=None, description="NOFOs and supplemental documents"
    )
    federal_funding_source: Optional[CustomField[str]] = Field(
        default=None, description="Category type (from source category field)"
    )
    contact_info: Optional[CustomField[ContactInfoValue]] = Field(
        default=None, description="Agency contact email and description"
    )
    additional_info: Optional[CustomField[AdditionalInfoValue]] = Field(
        default=None, description="URL and description for additional info"
    )
    fiscal_year: Optional[CustomField[int]] = Field(
        default=None, description="Fiscal year for the opportunity"
    )
    cost_sharing: Optional[CustomField[CostSharingValue]] = Field(
        default=None, description="Whether cost sharing is required"
    )
    funding_instruments: Optional[CustomField[list[str]]] = Field(
        default=None, description="Funding instrument types"
    )
    funding_categories: Optional[CustomField[list[str]]] = Field(
        default=None, description="Funding category types"
    )
    funding_category_description: Optional[CustomField[str]] = Field(
        default=None, description="Free-text description of the funding category"
    )
    applicant_eligibility_description: Optional[CustomField[str]] = Field(
        default=None, description="Free-text description of eligible applicants"
    )
    version_number: Optional[CustomField[int]] = Field(
        default=None, description="Opportunity summary version number"
    )
    category_explanation: Optional[CustomField[str]] = Field(
        default=None, description="Explanation when category is 'other'"
    )
    competitions: Optional[CustomField[list[CompetitionValue]]] = Field(
        default=None, description="Competitions associated with the opportunity"
    )
    agency_email_address_description: Optional[CustomField[str]] = Field(
        default=None, description="Link text for the agency email address"
    )
    summary_created_at: Optional[CustomField[str]] = Field(
        default=None, description="Timestamp when the opportunity summary was created"
    )
    summary_updated_at: Optional[CustomField[str]] = Field(
        default=None,
        description="Timestamp when the opportunity summary was last updated",
    )


# =============================================================================
# Section 3: Source schemas (GrantsGovOpportunitySchema and nested models)
# =============================================================================


class AssistanceListingSource(BaseModel):
    assistance_listing_number: Optional[str] = None
    program_title: Optional[str] = None


class AttachmentSource(BaseModel):
    opportunity_attachment_id: Optional[UUID] = None
    mime_type: Optional[str] = None
    file_name: Optional[str] = None
    file_description: Optional[str] = None
    download_path: Optional[str] = None
    file_size_bytes: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CompetitionSource(BaseModel):
    competition_id: UUID
    opportunity_id: UUID
    competition_title: Optional[str] = None


class OpportunitySummarySource(BaseModel):
    summary_description: Optional[str] = None
    is_cost_sharing: Optional[bool] = None
    is_forecast: bool
    close_date: Optional[date] = None
    close_date_description: Optional[str] = None
    post_date: Optional[date] = None
    archive_date: Optional[date] = None
    expected_number_of_awards: Optional[int] = None
    estimated_total_program_funding: Optional[int] = None
    award_floor: Optional[int] = None
    award_ceiling: Optional[int] = None
    additional_info_url: Optional[str] = None
    additional_info_url_description: Optional[str] = None
    forecasted_post_date: Optional[date] = None
    forecasted_close_date: Optional[date] = None
    forecasted_close_date_description: Optional[str] = None
    forecasted_award_date: Optional[date] = None
    forecasted_project_start_date: Optional[date] = None
    fiscal_year: Optional[int] = None
    funding_category_description: Optional[str] = None
    applicant_eligibility_description: Optional[str] = None
    agency_contact_description: Optional[str] = None
    agency_email_address: Optional[str] = None
    agency_email_address_description: Optional[str] = None
    version_number: Optional[int] = None
    funding_instruments: list[str] = Field(default_factory=list)
    funding_categories: list[str] = Field(default_factory=list)
    applicant_types: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class GrantsGovOpportunitySchema(BaseModel):
    opportunity_id: UUID
    legacy_opportunity_id: Optional[int] = None
    opportunity_number: Optional[str] = None
    opportunity_title: Optional[str] = None
    agency: Optional[str] = (
        None  # deprecated top-level code; preserved via legacyAgencyCode custom field
    )
    agency_code: Optional[str] = None
    agency_name: Optional[str] = None
    top_level_agency_name: Optional[str] = None
    top_level_agency_code: Optional[str] = None
    category: Optional[str] = None
    category_explanation: Optional[str] = None
    opportunity_assistance_listings: list[AssistanceListingSource] = Field(
        default_factory=list
    )
    summary: Optional[OpportunitySummarySource] = None
    opportunity_status: str  # "forecasted" | "posted" | "closed" | "archived"
    attachments: Optional[list[AttachmentSource]] = None
    competitions: Optional[list[CompetitionSource]] = None
    created_at: datetime
    updated_at: datetime
