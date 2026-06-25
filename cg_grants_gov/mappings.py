"""Status and applicant-type mapping dicts for the Grants.gov plugin."""

from __future__ import annotations

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
