"""Tests for Grants.gov plugin custom filter routes (#901).

The plugin registers the Simpler.Grants.gov search custom filters on
``opportunities.search`` so consumers get typed, validated filters rather than
ad-hoc passthrough. The set aligns with the filters the SGG API accepts:
agency / applicantType / fundingInstrument / costSharing.
"""

from typing import get_type_hints

import pytest

from common_grants_sdk.extensions import FilterError, classify_filters, f

from cg_grants_gov import grants_gov

REGISTERED_FILTERS = {"agency", "applicantType", "fundingInstrument", "costSharing"}


def test_registers_sgg_custom_filters_on_opportunities_search():
    search = grants_gov.routes.opportunities.search
    assert search is not None, "opportunities.search has no registered filter routes"
    assert REGISTERED_FILTERS <= set(get_type_hints(search))


def test_registered_filter_type_is_validated():
    # costSharing is registered as a BooleanComparison. Passing an array-operator
    # value is rejected fail-fast: classify_filters raises FilterError before any
    # request. An UNREGISTERED (ad-hoc) key passes silently, so this only holds
    # because the filter is actually registered and typed — the value the plugin adds.
    with pytest.raises(FilterError):
        classify_filters(
            grants_gov.routes,
            "opportunities",
            "search",
            {"costSharing": f.in_(["not-a-bool"])},
        )
