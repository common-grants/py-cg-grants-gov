"""Tests for Grants.gov plugin custom filter routes (#901).

The plugin registers the Simpler.Grants.gov search custom filters on
``opportunities.search`` so consumers get typed, validated filters rather than
ad-hoc passthrough. The set aligns with the filters the SGG API accepts:
agency / applicantType / fundingInstrument / costSharing.
"""

from typing import get_type_hints
from unittest.mock import Mock

import pytest

from common_grants_sdk.client import Auth, Config
from common_grants_sdk.extensions import FilterError, f

from cg_grants_gov import grants_gov

REGISTERED_FILTERS = {"agency", "applicantType", "fundingInstrument", "costSharing"}

BASE_URL = "https://api.example.test"


def _make_client():
    """Build the plugin's scoped client with a mocked HTTP transport.

    ``grants_gov.get_client`` binds the plugin's registered filters and
    Opportunity schema; swapping ``client.http`` for a ``Mock`` keeps the whole
    classify -> request -> parse path real while never touching the network.
    """
    client = grants_gov.get_client(
        Config(base_url=BASE_URL, api_key="test-key", page_size=5),
        Auth.api_key("test-key"),
    )
    client.http = Mock()
    return client


def _envelope(items: list[dict]) -> dict:
    """A minimal valid CommonGrants ``Filtered`` search envelope."""
    return {
        "status": 200,
        "message": "Success",
        "items": items,
        "paginationInfo": {
            "page": 1,
            "pageSize": max(len(items), 1),
            "totalItems": len(items),
            "totalPages": 1,
        },
        "sortInfo": {"sortBy": "lastModifiedAt", "sortOrder": "desc"},
        "filterInfo": {"filters": {}, "errors": []},
    }


def _stub_response(client, envelope: dict) -> None:
    """Make the mocked transport's POST return ``envelope`` as JSON."""
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = envelope
    client.http.post.return_value = response


OPPORTUNITY_WITH_AGENCY = {
    "id": "573525f2-8e15-4405-83fb-e6523511d893",
    "title": "STEM Education Grant Program",
    "description": "A grant program focused on STEM education.",
    "status": {"value": "open"},
    "createdAt": "2025-01-01T00:00:00Z",
    "lastModifiedAt": "2025-01-15T00:00:00Z",
    "customFields": {
        "agency": {
            "name": "agency",
            "fieldType": "object",
            "value": {
                "code": "HHS",
                "name": "Department of Health and Human Services",
            },
        },
    },
}


def test_registers_sgg_custom_filters_on_opportunities_search():
    search = grants_gov.routes.opportunities.search
    assert search is not None, "opportunities.search has no registered filter routes"
    assert REGISTERED_FILTERS <= set(get_type_hints(search))


def test_search_sends_all_registered_custom_filters_on_the_wire():
    # Drive the real scoped client: search(filters=...) classifies through the
    # bound routes and posts the request. Assert the wire body carries every
    # registered custom filter with its operator and value.
    client = _make_client()
    _stub_response(client, _envelope([]))

    client.opportunities.search(
        filters={
            "status": f.in_(["open"]),
            "agency": f.in_(["NSF"]),
            "applicantType": f.in_(["state_governments"]),
            "fundingInstrument": f.in_(["grant"]),
            "costSharing": f.eq(False),
        },
        page=1,
    )

    client.http.post.assert_called_once()
    call = client.http.post.call_args
    assert call.args[0] == f"{BASE_URL}/common-grants/opportunities/search"

    expected_custom_filters = {
        "agency": {"operator": "in", "value": ["NSF"]},
        "applicantType": {"operator": "in", "value": ["state_governments"]},
        "fundingInstrument": {"operator": "in", "value": ["grant"]},
        "costSharing": {"operator": "eq", "value": False},
    }
    assert call.kwargs["json"]["filters"]["customFilters"] == expected_custom_filters


def test_search_parses_grants_gov_custom_fields_via_bound_schema():
    # A returned opportunity with Grants.gov custom fields parses through the
    # plugin's bound Opportunity schema, so typed attribute access works.
    client = _make_client()
    _stub_response(client, _envelope([OPPORTUNITY_WITH_AGENCY]))

    result = client.opportunities.search(filters={"status": f.in_(["open"])}, page=1)

    assert not result.errors
    assert len(result.items) == 1
    assert result.items[0].custom_fields.agency.value.code == "HHS"


def test_invalid_registered_filter_value_raises_before_transport():
    # costSharing is a BooleanComparison; an array-operator value is rejected
    # fail-fast during classification, before any request is sent.
    client = _make_client()

    with pytest.raises(FilterError):
        client.opportunities.search(
            filters={"costSharing": f.in_(["not-a-bool"])}, page=1
        )

    client.http.post.assert_not_called()
