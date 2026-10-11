from backend.credence_gov.api import CaseAPI, CaseCreateRequest


def test_case_api_create_case_returns_safe_payload() -> None:
    api = CaseAPI()
    payload = api.create_case(
        CaseCreateRequest(
            tenant_id="tenant-010",
            owner_id="analyst-010",
            classification="restricted",
            title="Synthetic case",
            purpose="local validation only",
            as_of_date="2026-10-09",
        )
    )

    assert payload["tenant_id"] == "tenant-010"
    assert payload["classification"] == "restricted"
    assert payload["schema_version"] == 1
    assert payload["banner"] == "Decision support. Not a finding of fact."


def test_case_api_rejects_blank_case_titles() -> None:
    api = CaseAPI()

    try:
        api.create_case(
            CaseCreateRequest(
                tenant_id="tenant-011",
                owner_id="analyst-011",
                classification="restricted",
                title="   ",
                purpose="local validation only",
                as_of_date="2026-10-09",
            )
        )
        raise AssertionError("Expected ValueError")
    except ValueError as exc:
        assert "title" in str(exc).lower()
