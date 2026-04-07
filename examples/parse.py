from cg_grants_gov import grants_gov

opp_raw = {
    "id": "573525f2-8e15-4405-83fb-e6523511d893",
    "title": "STEM Education Grant Program",
    "description": "A grant program focused on STEM education in underserved communities",
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
                "parentName": None,
                "parentCode": None,
            },
        },
        "assistanceListings": {
            "name": "assistanceListings",
            "fieldType": "array",
            "value": [
                {"identifier": "93.123", "programTitle": "STEM Education"},
                {"identifier": "93.456", "programTitle": "Youth Development"},
            ],
        },
        "contactInfo": {
            "name": "contactInfo",
            "fieldType": "object",
            "value": {
                "name": "Jane Doe",
                "email": "jane.doe@hhs.gov",
                "phone": "555-0100",
                "description": "Program Officer",
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
            "value": {"isRequired": False},
        },
    },
}

opp = grants_gov.schemas.Opportunity.model_validate(opp_raw)

# Print the opportunity
print("opp.id:", opp.id)
print("  title:", opp.title)
print("  description:", opp.description)
print("  status:", opp.status.value)
print("  agency:", opp.custom_fields.agency.value.name)
print("  assistanceListings:", opp.custom_fields.assistance_listings.value)
print("  contactInfo:", opp.custom_fields.contact_info.value.name)
print("  fiscalYear:", opp.custom_fields.fiscal_year.value)
print("  costSharing:", opp.custom_fields.cost_sharing.value.isRequired)
