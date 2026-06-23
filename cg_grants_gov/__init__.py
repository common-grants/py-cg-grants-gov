"""Grants.gov CommonGrants plugin.

Maps GET /v1/opportunities/:id (OpportunityWithAttachmentsV1Schema)
to and from the CommonGrants OpportunityBase format.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from common_grants_sdk import define_plugin, PluginSchemas, schema
from common_grants_sdk.extensions import (
    CustomField,
    CustomFieldSet,
    PluginMeta,
    TransformResult,
    validate_into,
)
from common_grants_sdk.schemas.pydantic.fields.event import EventType, SingleDateEvent
from common_grants_sdk.schemas.pydantic.models import OpportunityBase
from common_grants_sdk.schemas.pydantic.models.opp_applicant_type import (
    ApplicantType,
    ApplicantTypeOptions,
)

# =============================================================================
# Section 1: Value schemas
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


# =============================================================================
# Section 3: Source schema (GrantsGovOpportunitySchema)
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
    agency: Optional[str] = None  # deprecated — parsed but not mapped in to_common
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


# =============================================================================
# Section 4: Mapping dicts
# =============================================================================

STATUS_TO_COMMON: dict[str, str] = {
    "forecasted": "forecasted",
    "posted": "open",
    "closed": "closed",
    "archived": "closed",
}

STATUS_FROM_COMMON: dict[str, str] = {
    "forecasted": "forecasted",
    "open": "posted",
    "closed": "closed",
    "custom": "posted",
}

# Maps v1 applicant_types strings → ApplicantTypeOptions values
APPLICANT_TYPE_TO_COMMON: dict[str, str] = {
    "state_governments": "government_state",
    "county_governments": "government_county",
    "city_or_township_governments": "government_municipal",
    "special_district_governments": "government_special_district",
    "independent_school_districts": "school_district_independent",
    "public_and_state_institutions_of_higher_education": "higher_education_public",
    "private_institutions_of_higher_education": "higher_education_private",
    "federally_recognized_native_american_tribal_governments": "government_tribal",
    "other_native_american_tribal_organizations": "organization_tribal_other",
    "nonprofits_non_higher_education_with_501c3": "non_profit_with_501c3",
    "nonprofits_non_higher_education_without_501c3": "nonprofit_without_501c3",
    "individuals": "individual",
    "for_profit_organizations_other_than_small_businesses": "for_profit_not_small_business",
    "small_businesses": "for_profit_small_business",
    "unrestricted": "unrestricted",
}

# Maps ApplicantTypeOptions values → v1 applicant_types strings
APPLICANT_TYPE_FROM_COMMON: dict[str, str] = {
    "individual": "individuals",
    "organization": "other",
    "government_state": "state_governments",
    "government_county": "county_governments",
    "government_municipal": "city_or_township_governments",
    "government_special_district": "special_district_governments",
    "government_tribal": "federally_recognized_native_american_tribal_governments",
    "organization_tribal_other": "other_native_american_tribal_organizations",
    "school_district_independent": "independent_school_districts",
    "higher_education_public": "public_and_state_institutions_of_higher_education",
    "higher_education_private": "private_institutions_of_higher_education",
    "non_profit_with_501c3": "nonprofits_non_higher_education_with_501c3",
    "nonprofit_without_501c3": "nonprofits_non_higher_education_without_501c3",
    "for_profit_small_business": "small_businesses",
    "for_profit_not_small_business": "for_profit_organizations_other_than_small_businesses",
    "unrestricted": "unrestricted",
    "custom": "other",
}


# =============================================================================
# Section 5: to_common transform
# =============================================================================


def _cf(name: str, field_type: str, value) -> dict:
    """Build a CustomField wire-format dict for the customFields payload."""
    return {"name": name, "fieldType": field_type, "value": value}


def to_common(
    native: GrantsGovOpportunitySchema | dict,
) -> TransformResult[OpportunityBase[OpportunityFields]]:
    """Transform a Grants.gov opportunity dict to CommonGrants format."""
    if isinstance(native, dict):
        native = GrantsGovOpportunitySchema.model_validate(native)

    summary = native.summary

    # Build funding dict
    funding: dict = {}
    if summary and summary.estimated_total_program_funding is not None:
        funding["totalAmountAvailable"] = {
            "amount": str(summary.estimated_total_program_funding),
            "currency": "USD",
        }
    if summary and summary.award_floor is not None:
        funding["minAwardAmount"] = {
            "amount": str(summary.award_floor),
            "currency": "USD",
        }
    if summary and summary.award_ceiling is not None:
        funding["maxAwardAmount"] = {
            "amount": str(summary.award_ceiling),
            "currency": "USD",
        }
    if summary and summary.expected_number_of_awards is not None:
        funding["estimatedAwardCount"] = summary.expected_number_of_awards

    # Build key_dates dict
    other_dates: dict = {}
    if summary:
        if summary.archive_date is not None:
            other_dates["archiveDate"] = SingleDateEvent(
                name="Archive Date",
                event_type=EventType.SINGLE_DATE,
                date=summary.archive_date,
            )
        if summary.forecasted_post_date is not None:
            other_dates["forecastedPostDate"] = SingleDateEvent(
                name="Forecasted Post Date",
                event_type=EventType.SINGLE_DATE,
                date=summary.forecasted_post_date,
            )
        if summary.forecasted_close_date is not None:
            other_dates["forecastedCloseDate"] = SingleDateEvent(
                name="Forecasted Close Date",
                event_type=EventType.SINGLE_DATE,
                date=summary.forecasted_close_date,
                description=summary.forecasted_close_date_description,
            )
        if summary.forecasted_award_date is not None:
            other_dates["forecastedAwardDate"] = SingleDateEvent(
                name="Forecasted Award Date",
                event_type=EventType.SINGLE_DATE,
                date=summary.forecasted_award_date,
            )
        if summary.forecasted_project_start_date is not None:
            other_dates["forecastedProjectStartDate"] = SingleDateEvent(
                name="Forecasted Project Start Date",
                event_type=EventType.SINGLE_DATE,
                date=summary.forecasted_project_start_date,
            )

    key_dates: dict = {}
    if summary and summary.post_date is not None:
        key_dates["postDate"] = SingleDateEvent(
            name="Post Date",
            event_type=EventType.SINGLE_DATE,
            date=summary.post_date,
        )
    if summary and summary.close_date is not None:
        key_dates["closeDate"] = SingleDateEvent(
            name="Close Date",
            event_type=EventType.SINGLE_DATE,
            date=summary.close_date,
            description=summary.close_date_description,
        )
    if other_dates:
        key_dates["otherDates"] = other_dates

    # Build accepted_applicant_types list
    accepted_applicant_types = []
    if summary:
        for raw in summary.applicant_types:
            mapped = APPLICANT_TYPE_TO_COMMON.get(raw)
            if mapped:
                accepted_applicant_types.append(
                    ApplicantType(value=ApplicantTypeOptions(mapped))
                )
            else:
                accepted_applicant_types.append(
                    ApplicantType(
                        value=ApplicantTypeOptions.custom,
                        custom_value=raw,
                    )
                )

    # Build customFields dict (wire format: {"name":..., "fieldType":..., "value":...})
    custom_fields: dict = {}
    if native.legacy_opportunity_id is not None:
        custom_fields["legacySerialId"] = _cf(
            "legacySerialId", "integer", native.legacy_opportunity_id
        )
    if native.opportunity_number is not None:
        custom_fields["federalOpportunityNumber"] = _cf(
            "federalOpportunityNumber", "string", native.opportunity_number
        )
    if native.opportunity_assistance_listings:
        custom_fields["assistanceListings"] = _cf(
            "assistanceListings",
            "array",
            [
                {
                    "identifier": al.assistance_listing_number,
                    "programTitle": al.program_title,
                }
                for al in native.opportunity_assistance_listings
            ],
        )
    custom_fields["agency"] = _cf(
        "agency",
        "object",
        {
            "code": native.agency_code,
            "name": native.agency_name,
            "parentName": native.top_level_agency_name,
            "parentCode": native.top_level_agency_code,
        },
    )
    if native.attachments:
        custom_fields["attachments"] = _cf(
            "attachments",
            "array",
            [
                {
                    "opportunityAttachmentId": str(a.opportunity_attachment_id) if a.opportunity_attachment_id else None,
                    "downloadUrl": a.download_path,
                    "name": a.file_name or "",
                    "description": a.file_description,
                    "sizeInBytes": a.file_size_bytes,
                    "mimeType": a.mime_type,
                    "createdAt": (a.created_at or native.created_at).isoformat(),
                    "lastModifiedAt": (a.updated_at or native.updated_at).isoformat(),
                }
                for a in native.attachments
            ],
        )
    if native.category is not None:
        custom_fields["federalFundingSource"] = _cf(
            "federalFundingSource", "string", native.category
        )
    if summary:
        if (
            summary.agency_email_address is not None
            or summary.agency_contact_description is not None
        ):
            custom_fields["contactInfo"] = _cf(
                "contactInfo",
                "object",
                {
                    "name": None,
                    "email": summary.agency_email_address,
                    "phone": None,
                    "description": summary.agency_contact_description,
                },
            )
        if (
            summary.additional_info_url is not None
            or summary.additional_info_url_description is not None
        ):
            custom_fields["additionalInfo"] = _cf(
                "additionalInfo",
                "object",
                {
                    "url": summary.additional_info_url,
                    "description": summary.additional_info_url_description,
                },
            )
        if summary.fiscal_year is not None:
            custom_fields["fiscalYear"] = _cf(
                "fiscalYear", "integer", summary.fiscal_year
            )
        if summary.is_cost_sharing is not None:
            custom_fields["costSharing"] = _cf(
                "costSharing", "object", {"isRequired": summary.is_cost_sharing}
            )
        if summary.funding_instruments:
            custom_fields["fundingInstruments"] = _cf(
                "fundingInstruments", "array", summary.funding_instruments
            )
        if summary.funding_categories:
            custom_fields["fundingCategories"] = _cf(
                "fundingCategories", "array", summary.funding_categories
            )
        if summary.funding_category_description is not None:
            custom_fields["fundingCategoryDescription"] = _cf(
                "fundingCategoryDescription",
                "string",
                summary.funding_category_description,
            )
        if summary.applicant_eligibility_description is not None:
            custom_fields["applicantEligibilityDescription"] = _cf(
                "applicantEligibilityDescription",
                "string",
                summary.applicant_eligibility_description,
            )
        if summary.version_number is not None:
            custom_fields["versionNumber"] = _cf(
                "versionNumber", "integer", summary.version_number
            )
        if summary.agency_email_address_description is not None:
            custom_fields["agencyEmailAddressDescription"] = _cf(
                "agencyEmailAddressDescription",
                "string",
                summary.agency_email_address_description,
            )
    if native.category_explanation is not None:
        custom_fields["categoryExplanation"] = _cf(
            "categoryExplanation", "string", native.category_explanation
        )
    if native.competitions:
        custom_fields["competitions"] = _cf(
            "competitions",
            "array",
            [
                {
                    "competitionId": str(c.competition_id),
                    "opportunityId": str(c.opportunity_id),
                    "competitionTitle": c.competition_title,
                }
                for c in native.competitions
            ],
        )

    # Assemble payload for OpportunityBase
    payload: dict = {
        "id": str(native.opportunity_id),
        "title": native.opportunity_title or "",
        "description": (summary.summary_description if summary else None) or "",
        "status": {"value": STATUS_TO_COMMON.get(native.opportunity_status, "custom")},
        "createdAt": native.created_at.isoformat(),
        "lastModifiedAt": native.updated_at.isoformat(),
    }
    if funding:
        payload["funding"] = funding
    if key_dates:
        payload["keyDates"] = key_dates
    if accepted_applicant_types:
        payload["acceptedApplicantTypes"] = [
            at.model_dump(by_alias=True) for at in accepted_applicant_types
        ]
    if custom_fields:
        payload["customFields"] = custom_fields

    return validate_into(OpportunityBase[OpportunityFields], payload)


# =============================================================================
# Section 6: from_common transform
# =============================================================================


def from_common(
    common: OpportunityBase[OpportunityFields] | dict,
) -> TransformResult[GrantsGovOpportunitySchema]:
    """Transform a CommonGrants opportunity to Grants.gov format."""
    if isinstance(common, dict):
        common = OpportunityBase[OpportunityFields].model_validate(common)

    # Derive opportunity_status first; is_forecast follows from it
    opportunity_status = STATUS_FROM_COMMON.get(common.status.value, "posted")
    is_forecast = opportunity_status == "forecasted"
    cf = common.custom_fields

    def _date_str(d) -> Optional[str]:
        if d is None:
            return None
        return d.isoformat() if hasattr(d, "isoformat") else str(d)

    def _other_date(key: str) -> Optional[str]:
        if common.key_dates is None or common.key_dates.other_dates is None:
            return None
        event = common.key_dates.other_dates.get(key)
        return _date_str(event.date) if event else None

    def _other_description(key: str) -> Optional[str]:
        if common.key_dates is None or common.key_dates.other_dates is None:
            return None
        event = common.key_dates.other_dates.get(key)
        return event.description if event else None

    summary_payload: dict = {
        "summary_description": common.description,
        "is_forecast": is_forecast,
        "is_cost_sharing": (
            cf.cost_sharing.value.isRequired if cf and cf.cost_sharing else None
        ),
        "close_date": (
            _date_str(common.key_dates.close_date.date)
            if common.key_dates and common.key_dates.close_date
            else None
        ),
        "close_date_description": (
            common.key_dates.close_date.description
            if common.key_dates and common.key_dates.close_date
            else None
        ),
        "post_date": (
            _date_str(common.key_dates.post_date.date)
            if common.key_dates and common.key_dates.post_date
            else None
        ),
        "archive_date": _other_date("archiveDate"),
        "forecasted_post_date": _other_date("forecastedPostDate"),
        "forecasted_close_date": _other_date("forecastedCloseDate"),
        "forecasted_close_date_description": _other_description("forecastedCloseDate"),
        "forecasted_award_date": _other_date("forecastedAwardDate"),
        "forecasted_project_start_date": _other_date("forecastedProjectStartDate"),
        "expected_number_of_awards": (
            common.funding.estimated_award_count if common.funding else None
        ),
        "estimated_total_program_funding": (
            int(float(str(common.funding.total_amount_available.amount)))
            if common.funding and common.funding.total_amount_available
            else None
        ),
        "award_floor": (
            int(float(str(common.funding.min_award_amount.amount)))
            if common.funding and common.funding.min_award_amount
            else None
        ),
        "award_ceiling": (
            int(float(str(common.funding.max_award_amount.amount)))
            if common.funding and common.funding.max_award_amount
            else None
        ),
        "additional_info_url": (
            cf.additional_info.value.url if cf and cf.additional_info else None
        ),
        "additional_info_url_description": (
            cf.additional_info.value.description if cf and cf.additional_info else None
        ),
        "fiscal_year": cf.fiscal_year.value if cf and cf.fiscal_year else None,
        "funding_category_description": (
            cf.funding_category_description.value
            if cf and cf.funding_category_description
            else None
        ),
        "applicant_eligibility_description": (
            cf.applicant_eligibility_description.value
            if cf and cf.applicant_eligibility_description
            else None
        ),
        "agency_contact_description": (
            cf.contact_info.value.description if cf and cf.contact_info else None
        ),
        "agency_email_address": (
            cf.contact_info.value.email if cf and cf.contact_info else None
        ),
        "agency_email_address_description": (
            cf.agency_email_address_description.value
            if cf and cf.agency_email_address_description
            else None
        ),
        "version_number": cf.version_number.value if cf and cf.version_number else None,
        "funding_instruments": (
            cf.funding_instruments.value if cf and cf.funding_instruments else []
        ),
        "funding_categories": (
            cf.funding_categories.value if cf and cf.funding_categories else []
        ),
        "applicant_types": [
            (
                APPLICANT_TYPE_FROM_COMMON.get(at.value, "other")
                if at.value != ApplicantTypeOptions.custom
                else (at.custom_value or "other")
            )
            for at in (common.accepted_applicant_types or [])
        ],
        "created_at": common.created_at.isoformat(),
        "updated_at": common.last_modified_at.isoformat(),
    }

    payload: dict = {
        "opportunity_id": str(common.id),
        "opportunity_title": common.title,
        "legacy_opportunity_id": (
            cf.legacy_serial_id.value if cf and cf.legacy_serial_id else None
        ),
        "opportunity_number": (
            cf.federal_opportunity_number.value
            if cf and cf.federal_opportunity_number
            else None
        ),
        "agency": None,
        "agency_code": cf.agency.value.code if cf and cf.agency else None,
        "agency_name": cf.agency.value.name if cf and cf.agency else None,
        "top_level_agency_name": (
            cf.agency.value.parentName if cf and cf.agency else None
        ),
        "top_level_agency_code": (
            cf.agency.value.parentCode if cf and cf.agency else None
        ),
        "category": (
            cf.federal_funding_source.value if cf and cf.federal_funding_source else None
        ),
        "category_explanation": (
            cf.category_explanation.value if cf and cf.category_explanation else None
        ),
        "opportunity_status": opportunity_status,
        "opportunity_assistance_listings": [
            {
                "assistance_listing_number": al.identifier,
                "program_title": al.programTitle,
            }
            for al in (
                cf.assistance_listings.value if cf and cf.assistance_listings else []
            )
        ],
        "attachments": (
            [
                {
                    "opportunity_attachment_id": str(a.opportunityAttachmentId) if a.opportunityAttachmentId else None,
                    "mime_type": a.mimeType,
                    "file_name": a.name,
                    "file_description": a.description,
                    "download_path": a.downloadUrl,
                    "file_size_bytes": a.sizeInBytes,
                    "created_at": a.createdAt.isoformat(),
                    "updated_at": a.lastModifiedAt.isoformat(),
                }
                for a in (cf.attachments.value if cf and cf.attachments else [])
            ]
            or None
        ),
        "competitions": (
            [
                {
                    "competition_id": str(comp.competitionId),
                    "opportunity_id": str(comp.opportunityId),
                    "competition_title": comp.competitionTitle,
                }
                for comp in (cf.competitions.value if cf and cf.competitions else [])
            ]
            or None
        ),
        "created_at": common.created_at.isoformat(),
        "updated_at": common.last_modified_at.isoformat(),
        "summary": summary_payload,
    }

    return validate_into(GrantsGovOpportunitySchema, payload)


# =============================================================================
# Section 7: Plugin assembly
# =============================================================================

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
