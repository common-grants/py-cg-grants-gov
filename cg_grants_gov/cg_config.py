"""Plugin config for extending the opportunity base class.

Defines custom fields for the Opportunity model and registers them
with the CommonGrants SDK plugin framework.
"""

from datetime import datetime

from pydantic import BaseModel

from common_grants_sdk import define_plugin
from common_grants_sdk.extensions import CustomFieldSpec, SchemaExtensions
from common_grants_sdk.schemas.pydantic.fields.custom import CustomFieldType


class AssistanceListingValue(BaseModel):
    identifier: str | None = None
    programTitle: str | None = None


class AgencyValue(BaseModel):
    code: str | None = None
    name: str | None = None
    parentName: str | None = None
    parentCode: str | None = None


class AttachmentValue(BaseModel):
    downloadUrl: str | None = None
    name: str
    description: str | None = None
    sizeInBytes: int
    mimeType: str
    createdAt: datetime
    lastModifiedAt: datetime


class ContactInfoValue(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    description: str | None = None


class AdditionalInfoValue(BaseModel):
    url: str
    description: str | None = None


class CostSharingValue(BaseModel):
    isRequired: bool


# Extensions that enhance the Opportunity object
extensions: SchemaExtensions = {
    "Opportunity": {
        "legacySerialId": CustomFieldSpec(
            field_type=CustomFieldType.INTEGER,
            description="An integer ID for the opportunity, needed for compatibility with legacy systems",
        ),
        "federalOpportunityNumber": CustomFieldSpec(
            field_type=CustomFieldType.STRING,
            description="The federal opportunity number assigned to this grant opportunity",
        ),
        "assistanceListings": CustomFieldSpec(
            field_type=CustomFieldType.ARRAY,
            value=AssistanceListingValue,
            description="The assistance listing number and program title for this opportunity",
        ),
        "agency": CustomFieldSpec(
            field_type=CustomFieldType.OBJECT,
            value=AgencyValue,
            description="Information about the agency offering this opportunity",
        ),
        "attachments": CustomFieldSpec(
            field_type=CustomFieldType.ARRAY,
            value=AttachmentValue,
            description="Attachments such as NOFOs and supplemental documents for the opportunity",
        ),
        "federalFundingSource": CustomFieldSpec(
            field_type=CustomFieldType.STRING,
            description="The category type of the grant opportunity",
        ),
        "contactInfo": CustomFieldSpec(
            field_type=CustomFieldType.OBJECT,
            value=ContactInfoValue,
            description="Contact information (name, email, phone, description) for this resource",
        ),
        "additionalInfo": CustomFieldSpec(
            field_type=CustomFieldType.OBJECT,
            value=AdditionalInfoValue,
            description="URL and description for additional information about the opportunity",
        ),
        "fiscalYear": CustomFieldSpec(
            field_type=CustomFieldType.INTEGER,
            description="The fiscal year associated with this opportunity",
        ),
        "costSharing": CustomFieldSpec(
            field_type=CustomFieldType.OBJECT,
            value=CostSharingValue,
            description="Whether cost sharing or matching funds are required for this opportunity",
        ),
    },
}


config = define_plugin(extensions)
