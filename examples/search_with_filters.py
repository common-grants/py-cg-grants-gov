"""Example: exercise the Grants.gov plugin's custom search filters (#901)
against the live Simpler.Grants.gov API.

The plugin registers four custom filters on ``opportunities.search``:

    - agency            (StringArray)       -> f.in_([...])
    - applicantType     (StringArray)       -> f.in_([...])
    - fundingInstrument (StringArray)       -> f.in_([...])
    - costSharing       (BooleanComparison) -> f.eq(True | False)

Because the client comes from ``grants_gov.get_client()``, the plugin's
registered routes are baked in: ``search(filters=...)`` validates each value
against its declared filter model and, for wrong-typed values, raises
``FilterError`` fail-fast before any request is sent.

At runtime the server also echoes back the ``filter_info`` it applied, so you
can confirm the custom filters reached the wire and the live API accepts them.

Run with:

    export SGG_API_KEY="your-api-key"
    poetry run python examples/search_with_filters.py

Optionally override the base URL (defaults to the production API):

    export SGG_BASE_URL="https://api.simpler.grants.gov"
"""

from __future__ import annotations

import os
import sys
from collections.abc import Callable

from common_grants_sdk.client import Auth, Config, SearchResult
from common_grants_sdk.extensions import FilterError, f
from common_grants_sdk.schemas.pydantic.models import OpportunityBase

from cg_grants_gov import grants_gov
from cg_grants_gov.models import OpportunityFields

BASE_URL = os.environ.get("SGG_BASE_URL", "https://api.simpler.grants.gov")
API_KEY = os.environ.get("SGG_API_KEY")

if not API_KEY:
    print(
        "\n".join(
            [
                "SGG_API_KEY is not set.",
                "",
                "This example calls the live Simpler.Grants.gov API, which requires an API key.",
                "Set it and re-run:",
                "",
                '  export SGG_API_KEY="your-api-key"',
                "  poetry run python examples/search_with_filters.py",
                "",
                "Need a key? See https://api.simpler.grants.gov/docs",
            ]
        ),
        file=sys.stderr,
    )
    sys.exit(1)

# A parsed opportunity, with the plugin's Grants.gov custom fields typed.
Opportunity = OpportunityBase[OpportunityFields]

# The plugin binds its Opportunity schema and its registered routes/filters, so
# search(filters=...) is validated and typed by the plugin's custom filters.
client = grants_gov.get_client(
    Config(base_url=BASE_URL, page_size=5),
    Auth.api_key(API_KEY),
)


def log_opportunity(opp: Opportunity) -> None:
    """Print an opportunity's title and id, then the Grants.gov custom-field
    values beneath it. The plugin's bound schema parses each field into its
    typed model, so ``agency.value.name`` and friends are attribute access."""
    cf = opp.custom_fields
    print(f"  {opp.title} ({opp.id})")
    if cf is None:
        print("    (no custom fields parsed)")
        return
    agency = cf.agency.value if cf.agency else None
    print(
        f"    agency:             {agency.name if agency else None} ({agency.code if agency else None})"
    )
    print(
        f"    federalOppNumber:   {cf.federal_opportunity_number.value if cf.federal_opportunity_number else None}"
    )
    print(
        f"    legacySerialId:     {cf.legacy_serial_id.value if cf.legacy_serial_id else None}"
    )
    fi = cf.funding_instruments.value if cf.funding_instruments else None
    print(f"    fundingInstruments: {', '.join(fi) if fi else None}")
    listings = cf.assistance_listings.value if cf.assistance_listings else None
    print(f"    assistanceListings: {len(listings) if listings else 0}")


def run(label: str, search: Callable[[], SearchResult[Opportunity]]) -> None:
    """Run one search and print the outcome. Each scenario is isolated: a
    ``FilterError`` (bad local value) or an HTTP error is caught here so the
    remaining scenarios still run."""
    print(f"\n=== {label} ===")
    try:
        result = search()
        total = result.pagination_info.total_items
        print(f"  total matches:           {total}")
        print(f"  items returned (page 1): {len(result.items)}")
        print(f"  per-row parse failures:  {len(result.errors)}")
        # The server echoes the filters it applied; confirms the custom filters
        # reached the wire and were understood by the live API.
        echoed = result.filter_info.filters.model_dump(by_alias=True, exclude_none=True)
        print(f"  filterInfo echoed by API: {echoed}")
        if result.items:
            log_opportunity(result.items[0])
    except FilterError as e:
        print(f"  FilterError: {e}")
    except Exception as e:  # noqa: BLE001 - example: surface any API/network error
        print(f"  ERROR: {e}")


def main() -> None:
    print(f"Base URL: {BASE_URL}")
    search = grants_gov.routes.opportunities.search
    registered = [k for k in (search.__annotations__ if search else {})]
    print(f"Registered custom filters: {', '.join(registered)}")

    # Baseline: no custom filters, just open opportunities. `status` is a default
    # filter; pass it through `filters` — the old `status=` shorthand is deprecated.
    # `run` logs the first result's custom fields, confirming the plugin parsed
    # them out of the live response.
    run(
        "Baseline (open opportunities, no custom filters)",
        lambda: client.opportunities.search(
            filters={"status": f.in_(["open"])}, page=1
        ),
    )

    # Each registered custom filter, one at a time. Adjust the codes to ones the
    # live API recognizes; the point here is that the filter is registered,
    # validated, and accepted end to end.
    run(
        "agency (StringArray)",
        lambda: client.opportunities.search(
            filters={"status": f.in_(["open"]), "agency": f.in_(["NSF"])}, page=1
        ),
    )
    run(
        "applicantType (StringArray)",
        lambda: client.opportunities.search(
            filters={
                "status": f.in_(["open"]),
                "applicantType": f.in_(["state_governments"]),
            },
            page=1,
        ),
    )
    run(
        "fundingInstrument (StringArray)",
        lambda: client.opportunities.search(
            filters={"status": f.in_(["open"]), "fundingInstrument": f.in_(["grant"])},
            page=1,
        ),
    )
    run(
        "costSharing (BooleanComparison)",
        lambda: client.opportunities.search(
            filters={"status": f.in_(["open"]), "costSharing": f.eq(False)}, page=1
        ),
    )

    # All four together, to confirm they compose in a single request.
    run(
        "all four filters combined",
        lambda: client.opportunities.search(
            filters={
                "status": f.in_(["open"]),
                "agency": f.in_(["USAID"]),
                "applicantType": f.in_(["state_governments"]),
                "fundingInstrument": f.in_(["grant"]),
                "costSharing": f.eq(False),
            },
            page=1,
        ),
    )

    print("\n✓ search-with-filters example complete")


if __name__ == "__main__":
    main()
