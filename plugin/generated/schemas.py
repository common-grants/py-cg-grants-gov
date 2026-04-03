""" Pydantic schemas that will be exported as part of a plugin."""


from __future__ import annotations

from typing import Any, Optional

from pydantic import ConfigDict, Field

from common_grants_sdk.schemas.pydantic.base import CommonGrantsBaseModel
from common_grants_sdk.schemas.pydantic.fields import CustomField, CustomFieldType
from common_grants_sdk.schemas.pydantic.models import OpportunityBase


class OpportunityLegacySerialIdCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.INTEGER,
        alias="fieldType",
    )
    name: str = Field(default="legacySerialId")
    description: Optional[str] = Field(
        default="An integer ID for the opportunity, needed for compatibility with legacy systems"
    )
    value: Optional[int] = None


class OpportunityFederalOpportunityNumberCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.STRING,
        alias="fieldType",
    )
    name: str = Field(default="federalOpportunityNumber")
    description: Optional[str] = Field(
        default="The federal opportunity number assigned to this grant opportunity"
    )
    value: Optional[str] = None


class OpportunityAssistanceListingsCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.ARRAY,
        alias="fieldType",
    )
    name: str = Field(default="assistanceListings")
    description: Optional[str] = Field(
        default="The assistance listing number and program title for this opportunity"
    )
    value: Optional[list[str]] = None


class OpportunityAgencyCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.OBJECT,
        alias="fieldType",
    )
    name: str = Field(default="agency")
    description: Optional[str] = Field(
        default="Information about the agency offering this opportunity"
    )
    value: Optional[dict[str, Any]] = None


class OpportunityAttachmentsCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.ARRAY,
        alias="fieldType",
    )
    name: str = Field(default="attachments")
    description: Optional[str] = Field(
        default="Attachments such as NOFOs and supplemental documents for the opportunity"
    )
    value: Optional[list[str]] = None


class OpportunityFederalFundingSourceCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.STRING,
        alias="fieldType",
    )
    name: str = Field(default="federalFundingSource")
    description: Optional[str] = Field(
        default="The category type of the grant opportunity"
    )
    value: Optional[str] = None


class OpportunityContactInfoCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.OBJECT,
        alias="fieldType",
    )
    name: str = Field(default="contactInfo")
    description: Optional[str] = Field(
        default="Contact information (name, email, phone, description) for this resource"
    )
    value: Optional[dict[str, Any]] = None


class OpportunityAdditionalInfoCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.OBJECT,
        alias="fieldType",
    )
    name: str = Field(default="additionalInfo")
    description: Optional[str] = Field(
        default="URL and description for additional information about the opportunity"
    )
    value: Optional[dict[str, Any]] = None


class OpportunityFiscalYearCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.INTEGER,
        alias="fieldType",
    )
    name: str = Field(default="fiscalYear")
    description: Optional[str] = Field(
        default="The fiscal year associated with this opportunity"
    )
    value: Optional[int] = None


class OpportunityCostSharingCustomField(CustomField):
    model_config = ConfigDict(populate_by_name=True)
    field_type: CustomFieldType = Field(
        default=CustomFieldType.OBJECT,
        alias="fieldType",
    )
    name: str = Field(default="costSharing")
    description: Optional[str] = Field(
        default="Whether cost sharing or matching funds are required for this opportunity"
    )
    value: Optional[dict[str, Any]] = None


class OpportunityCustomFields(CommonGrantsBaseModel):
    model_config = ConfigDict(populate_by_name=True)
    legacy_serial_id: Optional[OpportunityLegacySerialIdCustomField] = Field(
        default=None,
        alias="legacySerialId",
    )
    federal_opportunity_number: Optional[
        OpportunityFederalOpportunityNumberCustomField
    ] = Field(
        default=None,
        alias="federalOpportunityNumber",
    )
    assistance_listings: Optional[OpportunityAssistanceListingsCustomField] = Field(
        default=None,
        alias="assistanceListings",
    )
    agency: Optional[OpportunityAgencyCustomField] = Field(
        default=None,
        alias="agency",
    )
    attachments: Optional[OpportunityAttachmentsCustomField] = Field(
        default=None,
        alias="attachments",
    )
    federal_funding_source: Optional[OpportunityFederalFundingSourceCustomField] = (
        Field(
            default=None,
            alias="federalFundingSource",
        )
    )
    contact_info: Optional[OpportunityContactInfoCustomField] = Field(
        default=None,
        alias="contactInfo",
    )
    additional_info: Optional[OpportunityAdditionalInfoCustomField] = Field(
        default=None,
        alias="additionalInfo",
    )
    fiscal_year: Optional[OpportunityFiscalYearCustomField] = Field(
        default=None,
        alias="fiscalYear",
    )
    cost_sharing: Optional[OpportunityCostSharingCustomField] = Field(
        default=None,
        alias="costSharing",
    )


class Opportunity(OpportunityBase):
    model_config = ConfigDict(populate_by_name=True)
    custom_fields: Optional[OpportunityCustomFields] = Field(  # type: ignore[assignment]
        default=None,
        alias="customFields",
    )


class _Schemas:
    def __init__(self) -> None:
        self.Opportunity = Opportunity


schemas = _Schemas()

__all__ = ["Opportunity", "schemas"]
