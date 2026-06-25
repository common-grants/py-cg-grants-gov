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
        result = schema.parse({**base_opportunity, "customFields": valid_custom_fields})

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
        result = schema.parse(base_opportunity)

        assert result.title == "STEM Education Grant Program"
        assert result.custom_fields is None


class TestMissingData:
    def test_accepts_nullish_values_in_agency_fields(self):
        result = schema.parse(
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
        result = schema.parse(
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

    def test_accepts_none_for_agency_code(self):
        result = schema.parse(
            {
                **base_opportunity,
                "customFields": {
                    "agency": {
                        "name": "agency",
                        "fieldType": "object",
                        "value": {
                            "code": None,
                            "name": "Department of Health and Human Services",
                        },
                    }
                },
            }
        )

        assert result.custom_fields.agency.value.code is None
        assert (
            result.custom_fields.agency.value.name
            == "Department of Health and Human Services"
        )

    def test_accepts_nullish_values_in_assistance_listing_fields(self):
        result = schema.parse(
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
            schema.parse(
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
        assert len(errors) == 3  # sizeInBytes and mimeType are now Optional
        for error in errors:
            assert error["type"] == "missing"
            assert error["msg"] == "Field required"

    def test_rejects_agency_code_with_wrong_type(self):
        with pytest.raises(ValidationError) as exc_info:
            schema.parse(
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
            schema.parse(
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
            schema.parse(
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
        result = schema.parse(
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
        result = schema.parse(
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


# =============================================================================
# Transform fixtures and tests
# =============================================================================

SOURCE_FIXTURE = {
    "opportunity_id": "573525f2-8e15-4405-83fb-e6523511d893",
    "legacy_opportunity_id": 12345,
    "opportunity_number": "HHS-2025-001",
    "opportunity_title": "STEM Education Grant Program",
    "agency": None,
    "agency_code": "HHS",
    "agency_name": "Department of Health and Human Services",
    "top_level_agency_name": "Department of Health",
    "top_level_agency_code": "HHS-PARENT",
    "category": "Discretionary",
    "category_explanation": None,
    "opportunity_status": "posted",
    "opportunity_assistance_listings": [
        {"assistance_listing_number": "93.123", "program_title": "STEM Education"}
    ],
    "attachments": [
        {
            "opportunity_attachment_id": "a1b2c3d4-0000-0000-0000-000000000001",
            "mime_type": "application/pdf",
            "file_name": "NOFO.pdf",
            "file_description": "Notice of Funding Opportunity",
            "download_path": "https://example.com/nofo.pdf",
            "file_size_bytes": 102400,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-10T00:00:00Z",
        }
    ],
    "competitions": [
        {
            "competition_id": "c1c2c3c4-0000-0000-0000-000000000001",
            "opportunity_id": "573525f2-8e15-4405-83fb-e6523511d893",
            "competition_title": "Phase 1",
        }
    ],
    "created_at": "2025-01-01T00:00:00Z",
    "updated_at": "2025-01-15T00:00:00Z",
    "summary": {
        "summary_description": "A grant program focused on STEM education",
        "is_cost_sharing": True,
        "is_forecast": False,
        "close_date": "2025-03-31",
        "close_date_description": "Applications close at 5pm ET",
        "post_date": "2025-01-01",
        "archive_date": "2025-06-30",
        "expected_number_of_awards": 10,
        "estimated_total_program_funding": 1000000,
        "award_floor": 50000,
        "award_ceiling": 200000,
        "additional_info_url": "https://example.com/info",
        "additional_info_url_description": "More details here",
        "forecasted_post_date": None,
        "forecasted_close_date": None,
        "forecasted_close_date_description": None,
        "forecasted_award_date": None,
        "forecasted_project_start_date": None,
        "fiscal_year": 2025,
        "funding_category_description": "Education programs",
        "applicant_eligibility_description": "Open to state governments",
        "agency_contact_description": "Contact program officer",
        "agency_email_address": "stem@hhs.gov",
        "agency_email_address_description": "Email us",
        "version_number": 3,
        "funding_instruments": ["grant", "cooperative_agreement"],
        "funding_categories": ["education"],
        "applicant_types": ["state_governments", "county_governments"],
        "created_at": "2025-01-01T00:00:00Z",
        "updated_at": "2025-01-15T00:00:00Z",
    },
}


class TestTransforms:
    def test_to_common_full_fixture(self):
        opp_schema = grants_gov.schemas.Opportunity
        result = opp_schema.to_common(SOURCE_FIXTURE)
        assert not result.errors, f"Unexpected errors: {result.errors}"
        common = result.result
        assert str(common.id) == "573525f2-8e15-4405-83fb-e6523511d893"
        assert common.title == "STEM Education Grant Program"
        assert common.status.value == "open"
        assert common.description == "A grant program focused on STEM education"
        cf = common.custom_fields
        assert cf.legacy_serial_id.value == 12345
        assert cf.federal_opportunity_number.value == "HHS-2025-001"
        assert cf.agency.value.code == "HHS"
        assert cf.agency.value.parentName == "Department of Health"
        assert len(cf.assistance_listings.value) == 1
        assert len(cf.attachments.value) == 1
        assert cf.federal_funding_source.value == "Discretionary"
        assert cf.fiscal_year.value == 2025
        assert cf.cost_sharing.value.isRequired is True
        assert cf.funding_instruments.value == ["grant", "cooperative_agreement"]
        assert cf.funding_categories.value == ["education"]
        assert cf.version_number.value == 3
        assert len(cf.competitions.value) == 1

    def test_accepted_applicant_types_mapped(self):
        opp_schema = grants_gov.schemas.Opportunity
        result = opp_schema.to_common(SOURCE_FIXTURE)
        assert not result.errors
        common = result.result
        assert common.accepted_applicant_types is not None
        assert len(common.accepted_applicant_types) == 2
        values = [at.value for at in common.accepted_applicant_types]
        assert "government_state" in values
        assert "government_county" in values

    def test_other_dates_keys(self):
        opp_schema = grants_gov.schemas.Opportunity
        result = opp_schema.to_common(SOURCE_FIXTURE)
        assert not result.errors
        common = result.result
        assert common.key_dates is not None
        assert common.key_dates.post_date is not None
        assert str(common.key_dates.post_date.date) == "2025-01-01"
        assert common.key_dates.close_date is not None
        assert common.key_dates.other_dates is not None
        assert "archiveDate" in common.key_dates.other_dates

    def test_new_custom_fields_present(self):
        opp_schema = grants_gov.schemas.Opportunity
        result = opp_schema.to_common(SOURCE_FIXTURE)
        assert not result.errors
        cf = result.result.custom_fields
        assert cf.funding_instruments is not None
        assert cf.funding_categories is not None
        assert cf.competitions is not None

    def test_from_common_round_trip(self):
        opp_schema = grants_gov.schemas.Opportunity
        to_result = opp_schema.to_common(SOURCE_FIXTURE)
        assert not to_result.errors
        from_result = opp_schema.from_common(to_result.result)
        assert not from_result.errors, f"Unexpected errors: {from_result.errors}"
        source = from_result.result
        assert str(source.opportunity_id) == "573525f2-8e15-4405-83fb-e6523511d893"
        assert source.opportunity_title == "STEM Education Grant Program"
        assert source.opportunity_status == "posted"
        assert source.agency_code == "HHS"


# =============================================================================
# Comprehensive round-trip fixtures
# =============================================================================

# All posted-opportunity fields populated (category_explanation non-null)
FULL_FIXTURE = {
    **SOURCE_FIXTURE,
    "category_explanation": "Other federal funding mechanism",
}

# Forecasted opportunity with all forecast-only date fields populated
FORECAST_FIXTURE = {
    **SOURCE_FIXTURE,
    "opportunity_status": "forecasted",
    "summary": {
        **SOURCE_FIXTURE["summary"],
        "is_forecast": True,
        "close_date": None,
        "close_date_description": None,
        "post_date": None,
        "forecasted_post_date": "2025-03-01",
        "forecasted_close_date": "2025-09-30",
        "forecasted_close_date_description": "Expected to close in late September",
        "forecasted_award_date": "2025-12-01",
        "forecasted_project_start_date": "2026-01-01",
    },
}


class TestFieldRoundTrip:
    """Validates every field from GET /v1/opportunities/:id survives to_common → from_common."""

    def _roundtrip(self, fixture):
        opp_schema = grants_gov.schemas.Opportunity
        to_result = opp_schema.to_common(fixture)
        assert not to_result.errors, f"to_common errors: {to_result.errors}"
        from_result = opp_schema.from_common(to_result.result)
        assert not from_result.errors, f"from_common errors: {from_result.errors}"
        return from_result.result

    def test_top_level_fields(self):
        src = self._roundtrip(FULL_FIXTURE)
        assert str(src.opportunity_id) == FULL_FIXTURE["opportunity_id"]
        assert src.legacy_opportunity_id == FULL_FIXTURE["legacy_opportunity_id"]
        assert src.opportunity_number == FULL_FIXTURE["opportunity_number"]
        assert src.opportunity_title == FULL_FIXTURE["opportunity_title"]
        assert src.agency_code == FULL_FIXTURE["agency_code"]
        assert src.agency_name == FULL_FIXTURE["agency_name"]
        assert src.top_level_agency_name == FULL_FIXTURE["top_level_agency_name"]
        assert src.top_level_agency_code == FULL_FIXTURE["top_level_agency_code"]
        assert src.category == FULL_FIXTURE["category"]
        assert src.category_explanation == FULL_FIXTURE["category_explanation"]
        assert src.opportunity_status == FULL_FIXTURE["opportunity_status"]

    def test_assistance_listings(self):
        src = self._roundtrip(FULL_FIXTURE)
        assert len(src.opportunity_assistance_listings) == 1
        al = src.opportunity_assistance_listings[0]
        assert al.assistance_listing_number == "93.123"
        assert al.program_title == "STEM Education"

    def test_summary_scalar_fields(self):
        src = self._roundtrip(FULL_FIXTURE)
        s = src.summary
        assert s.summary_description == FULL_FIXTURE["summary"]["summary_description"]
        assert s.is_cost_sharing == FULL_FIXTURE["summary"]["is_cost_sharing"]
        assert s.is_forecast == FULL_FIXTURE["summary"]["is_forecast"]
        assert str(s.close_date) == FULL_FIXTURE["summary"]["close_date"]
        assert (
            s.close_date_description
            == FULL_FIXTURE["summary"]["close_date_description"]
        )
        assert str(s.post_date) == FULL_FIXTURE["summary"]["post_date"]
        assert str(s.archive_date) == FULL_FIXTURE["summary"]["archive_date"]
        assert (
            s.expected_number_of_awards
            == FULL_FIXTURE["summary"]["expected_number_of_awards"]
        )
        assert (
            s.estimated_total_program_funding
            == FULL_FIXTURE["summary"]["estimated_total_program_funding"]
        )
        assert s.award_floor == FULL_FIXTURE["summary"]["award_floor"]
        assert s.award_ceiling == FULL_FIXTURE["summary"]["award_ceiling"]
        assert s.additional_info_url == FULL_FIXTURE["summary"]["additional_info_url"]
        assert (
            s.additional_info_url_description
            == FULL_FIXTURE["summary"]["additional_info_url_description"]
        )
        assert s.fiscal_year == FULL_FIXTURE["summary"]["fiscal_year"]
        assert (
            s.funding_category_description
            == FULL_FIXTURE["summary"]["funding_category_description"]
        )
        assert (
            s.applicant_eligibility_description
            == FULL_FIXTURE["summary"]["applicant_eligibility_description"]
        )
        assert (
            s.agency_contact_description
            == FULL_FIXTURE["summary"]["agency_contact_description"]
        )
        assert s.agency_email_address == FULL_FIXTURE["summary"]["agency_email_address"]
        assert (
            s.agency_email_address_description
            == FULL_FIXTURE["summary"]["agency_email_address_description"]
        )
        assert s.version_number == FULL_FIXTURE["summary"]["version_number"]
        assert s.funding_instruments == FULL_FIXTURE["summary"]["funding_instruments"]
        assert s.funding_categories == FULL_FIXTURE["summary"]["funding_categories"]
        assert s.applicant_types == FULL_FIXTURE["summary"]["applicant_types"]

    def test_attachments(self):
        src = self._roundtrip(FULL_FIXTURE)
        assert len(src.attachments) == 1
        a = src.attachments[0]
        assert a.mime_type == "application/pdf"
        assert a.file_name == "NOFO.pdf"
        assert a.file_description == "Notice of Funding Opportunity"
        assert (
            str(a.opportunity_attachment_id) == "a1b2c3d4-0000-0000-0000-000000000001"
        )
        assert a.download_path == "https://example.com/nofo.pdf"
        assert a.file_size_bytes == 102400
        assert str(a.created_at.date()) == "2025-01-01"
        assert str(a.updated_at.date()) == "2025-01-10"

    def test_competitions(self):
        src = self._roundtrip(FULL_FIXTURE)
        assert len(src.competitions) == 1
        c = src.competitions[0]
        assert str(c.competition_id) == "c1c2c3c4-0000-0000-0000-000000000001"
        assert str(c.opportunity_id) == "573525f2-8e15-4405-83fb-e6523511d893"
        assert c.competition_title == "Phase 1"

    def test_forecasted_dates(self):
        src = self._roundtrip(FORECAST_FIXTURE)
        s = src.summary
        assert s.is_forecast is True
        assert (
            str(s.forecasted_post_date)
            == FORECAST_FIXTURE["summary"]["forecasted_post_date"]
        )
        assert (
            str(s.forecasted_close_date)
            == FORECAST_FIXTURE["summary"]["forecasted_close_date"]
        )
        assert (
            s.forecasted_close_date_description
            == FORECAST_FIXTURE["summary"]["forecasted_close_date_description"]
        )
        assert (
            str(s.forecasted_award_date)
            == FORECAST_FIXTURE["summary"]["forecasted_award_date"]
        )
        assert (
            str(s.forecasted_project_start_date)
            == FORECAST_FIXTURE["summary"]["forecasted_project_start_date"]
        )

    def test_agency_preserved_when_set(self):
        fixture = {**FULL_FIXTURE, "agency": "DOI-BOR-MP"}
        src = self._roundtrip(fixture)
        assert src.agency == "DOI-BOR-MP"

    def test_agency_none_when_not_set(self):
        src = self._roundtrip(FULL_FIXTURE)
        assert src.agency is None

    def test_empty_attachments_roundtrip(self):
        """Empty attachments list [] must survive round-trip as [] not None."""
        fixture = {**FULL_FIXTURE, "attachments": []}
        src = self._roundtrip(fixture)
        assert src.attachments == []

    def test_empty_competitions_roundtrip(self):
        """Empty competitions list [] must survive round-trip as [] not None."""
        fixture = {**FULL_FIXTURE, "competitions": []}
        src = self._roundtrip(fixture)
        assert src.competitions == []

    def test_absent_attachments_is_none(self):
        """Absent attachments key must round-trip back to None."""
        fixture = {k: v for k, v in FULL_FIXTURE.items() if k != "attachments"}
        src = self._roundtrip(fixture)
        assert src.attachments is None

    def test_absent_competitions_is_none(self):
        """Absent competitions key must round-trip back to None."""
        fixture = {k: v for k, v in FULL_FIXTURE.items() if k != "competitions"}
        src = self._roundtrip(fixture)
        assert src.competitions is None

    def test_summary_timestamps_preserved_separately(self):
        """Summary created_at/updated_at must be stored and restored independently
        from the top-level opportunity timestamps.

        The base fixtures share the same timestamps for both levels, so a bug that
        falls back to the top-level values would appear correct. This fixture uses
        deliberately different summary timestamps to catch that regression.
        """
        fixture = {
            **FULL_FIXTURE,
            "created_at": "2025-01-01T00:00:00Z",
            "updated_at": "2025-01-15T00:00:00Z",
            "summary": {
                **FULL_FIXTURE["summary"],
                "created_at": "2024-06-01T00:00:00Z",
                "updated_at": "2024-12-01T00:00:00Z",
            },
        }
        src = self._roundtrip(fixture)
        assert src.summary.created_at.year == 2024
        assert src.summary.created_at.month == 6
        assert src.summary.updated_at.year == 2024
        assert src.summary.updated_at.month == 12
