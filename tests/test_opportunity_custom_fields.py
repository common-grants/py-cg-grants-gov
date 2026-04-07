"""Tests for Grants.gov plugin Opportunity custom fields."""

import pytest
from pydantic import ValidationError

from cg_grants_gov import grants_gov

# =============================================================================
# Test Data
# =============================================================================

schema = grants_gov.schemas.Opportunity

base_opportunity = {
    "id": "573525f2-8e15-4405-83fb-e6523511d893",
    "title": "STEM Education Grant Program",
    "description": "A grant program focused on STEM education",
    "status": {"value": "open"},
    "createdAt": "2025-01-01T00:00:00Z",
    "lastModifiedAt": "2025-01-15T00:00:00Z",
}

valid_custom_fields = {
    "legacySerialId": {
        "name": "legacySerialId",
        "fieldType": "integer",
        "value": 12345,
    },
    "federalOpportunityNumber": {
        "name": "federalOpportunityNumber",
        "fieldType": "string",
        "value": "HHS-2025-001",
    },
    "assistanceListings": {
        "name": "assistanceListings",
        "fieldType": "array",
        "value": [{"identifier": "93.123", "programTitle": "STEM Education"}],
    },
    "agency": {
        "name": "agency",
        "fieldType": "object",
        "value": {
            "code": "HHS",
            "name": "Department of Health and Human Services",
            "parentName": None,
            "parentCode": None,
        },
    },
    "attachments": {
        "name": "attachments",
        "fieldType": "array",
        "value": [
            {
                "downloadUrl": "https://example.com/nofo.pdf",
                "name": "NOFO.pdf",
                "description": "Notice of Funding Opportunity",
                "sizeInBytes": 102400,
                "mimeType": "application/pdf",
                "createdAt": "2025-01-01T00:00:00Z",
                "lastModifiedAt": "2025-01-10T00:00:00Z",
            }
        ],
    },
    "federalFundingSource": {
        "name": "federalFundingSource",
        "fieldType": "string",
        "value": "Discretionary",
    },
    "contactInfo": {
        "name": "contactInfo",
        "fieldType": "object",
        "value": {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "555-0100",
            "description": "Program Officer",
        },
    },
    "additionalInfo": {
        "name": "additionalInfo",
        "fieldType": "object",
        "value": {
            "url": "https://example.com/info",
            "description": "More details",
        },
    },
    "fiscalYear": {
        "name": "fiscalYear",
        "fieldType": "integer",
        "value": 2025,
    },
    "costSharing": {
        "name": "costSharing",
        "fieldType": "object",
        "value": {"isRequired": True},
    },
}


# =============================================================================
# Tests
# =============================================================================


class TestExpectedData:
    def test_parses_opportunity_with_all_custom_fields(self):
        result = schema.model_validate(
            {**base_opportunity, "customFields": valid_custom_fields}
        )

        assert result.title == "STEM Education Grant Program"
        assert result.custom_fields.agency.value.code == "HHS"
        assert (
            result.custom_fields.agency.value.name
            == "Department of Health and Human Services"
        )
        assert result.custom_fields.agency.value.parentName is None
        assert result.custom_fields.agency.value.parentCode is None
        assert result.custom_fields.legacy_serial_id.value == 12345
        assert result.custom_fields.federal_opportunity_number.value == "HHS-2025-001"
        assert len(result.custom_fields.assistance_listings.value) == 1
        assert result.custom_fields.fiscal_year.value == 2025
        assert result.custom_fields.cost_sharing.value.isRequired is True

    def test_parses_opportunity_without_custom_fields(self):
        result = schema.model_validate(base_opportunity)

        assert result.title == "STEM Education Grant Program"
        assert result.custom_fields is None


class TestMissingData:
    def test_accepts_nullish_values_in_agency_fields(self):
        result = schema.model_validate(
            {
                **base_opportunity,
                "customFields": {
                    "agency": {
                        "name": "agency",
                        "fieldType": "object",
                        "value": {
                            "code": "HHS",
                            "name": None,
                            "parentName": None,
                            "parentCode": None,
                        },
                    }
                },
            }
        )

        assert result.custom_fields.agency.value.code == "HHS"
        assert result.custom_fields.agency.value.name is None

    def test_accepts_nullish_values_in_contact_info_fields(self):
        result = schema.model_validate(
            {
                **base_opportunity,
                "customFields": {
                    "contactInfo": {
                        "name": "contactInfo",
                        "fieldType": "object",
                        "value": {
                            "name": None,
                            "email": None,
                            "phone": None,
                            "description": None,
                        },
                    }
                },
            }
        )

        assert result.custom_fields.contact_info.value.name is None

    def test_accepts_nullish_values_in_assistance_listing_fields(self):
        result = schema.model_validate(
            {
                **base_opportunity,
                "customFields": {
                    "assistanceListings": {
                        "name": "assistanceListings",
                        "fieldType": "array",
                        "value": [{"identifier": None, "programTitle": None}],
                    }
                },
            }
        )

        assert result.custom_fields.assistance_listings.value[0].identifier is None


class TestInvalidData:
    def test_rejects_attachment_missing_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            schema.model_validate(
                {
                    **base_opportunity,
                    "customFields": {
                        "attachments": {
                            "name": "attachments",
                            "fieldType": "array",
                            "value": [
                                {
                                    "downloadUrl": "https://example.com/nofo.pdf",
                                    "description": "A document",
                                }
                            ],
                        }
                    },
                }
            )

        errors = exc_info.value.errors()
        error_locs = [e["loc"] for e in errors]
        assert ("customFields", "attachments", "value", 0, "name") in error_locs
        assert ("customFields", "attachments", "value", 0, "createdAt") in error_locs
        assert (
            "customFields",
            "attachments",
            "value",
            0,
            "lastModifiedAt",
        ) in error_locs
        for error in errors:
            assert error["type"] == "missing"
            assert error["msg"] == "Field required"

    def test_rejects_agency_with_wrong_type_for_required_field(self):
        with pytest.raises(ValidationError) as exc_info:
            schema.model_validate(
                {
                    **base_opportunity,
                    "customFields": {
                        "agency": {
                            "name": "agency",
                            "fieldType": "object",
                            "value": {"code": 123, "name": "HHS"},  # code should be str
                        }
                    },
                }
            )

        issue = exc_info.value.errors()[0]
        assert issue["type"] == "string_type"
        assert issue["loc"] == ("customFields", "agency", "value", "code")
        assert issue["msg"] == "Input should be a valid string"

    def test_rejects_attachment_with_invalid_datetime(self):
        with pytest.raises(ValidationError) as exc_info:
            schema.model_validate(
                {
                    **base_opportunity,
                    "customFields": {
                        "attachments": {
                            "name": "attachments",
                            "fieldType": "array",
                            "value": [
                                {
                                    "name": "file.pdf",
                                    "sizeInBytes": 100,
                                    "mimeType": "application/pdf",
                                    "createdAt": "not-a-date",
                                    "lastModifiedAt": "2025-01-01T00:00:00Z",
                                }
                            ],
                        }
                    },
                }
            )

        issue = exc_info.value.errors()[0]
        assert issue["type"] == "datetime_from_date_parsing"
        assert issue["loc"] == ("customFields", "attachments", "value", 0, "createdAt")

    def test_rejects_cost_sharing_value_with_wrong_type(self):
        with pytest.raises(ValidationError) as exc_info:
            schema.model_validate(
                {
                    **base_opportunity,
                    "customFields": {
                        "costSharing": {
                            "name": "costSharing",
                            "fieldType": "object",
                            "value": {"isRequired": "maybe"},  # should be bool
                        }
                    },
                }
            )

        issue = exc_info.value.errors()[0]
        assert issue["type"] == "bool_parsing"
        assert issue["loc"] == ("customFields", "costSharing", "value", "isRequired")
        assert (
            issue["msg"] == "Input should be a valid boolean, unable to interpret input"
        )


class TestExtraFields:
    def test_strips_extra_properties_from_custom_field_values(self):
        result = schema.model_validate(
            {
                **base_opportunity,
                "customFields": {
                    "agency": {
                        "name": "agency",
                        "fieldType": "object",
                        "value": {
                            "code": "HHS",
                            "name": "HHS",
                            "parentName": None,
                            "parentCode": None,
                            "extraProp": "should be stripped",
                        },
                    }
                },
            }
        )

        assert result.custom_fields.agency.value.code == "HHS"
        assert not hasattr(result.custom_fields.agency.value, "extraProp")

    def test_strips_unregistered_custom_fields(self):
        # NOTE: Unlike the TypeScript plugin which passes through unknown custom fields,
        # Pydantic strips fields not declared on OpportunityCustomFields by default.
        result = schema.model_validate(
            {
                **base_opportunity,
                "customFields": {
                    **valid_custom_fields,
                    "unknownField": {
                        "name": "unknownField",
                        "fieldType": "string",
                        "value": "extra data",
                    },
                },
            }
        )

        assert result.custom_fields.agency.value.code == "HHS"
        assert not hasattr(result.custom_fields, "unknownField")
