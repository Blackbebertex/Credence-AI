from backend.credence_gov.foundation import CaseService, EvidencePackage


def test_case_service_builds_safe_evidence_package() -> None:
    service = CaseService()
    case = service.create_case(
        tenant_id="tenant-001",
        owner_id="analyst-001",
        classification="restricted",
        title="Synthetic claim review",
    )

    package = service.build_evidence_package(
        case_id=case.id,
        case_title=case.title,
        claim="The document says a transaction occurred.",
        evidence_state="mixed",
        caveat="Only a synthetic record is being used for local validation.",
    )

    assert package.banner == "Decision support. Not a finding of fact."
    assert package.evidence_state == "mixed"
    assert "real" not in package.summary.lower()
    assert "fake" not in package.summary.lower()


def test_case_service_rejects_untrusted_verdicts() -> None:
    service = CaseService()
    case = service.create_case(
        tenant_id="tenant-002",
        owner_id="analyst-002",
        classification="open",
        title="Evidence package",
    )

    package = service.build_evidence_package(
        case_id=case.id,
        case_title=case.title,
        claim="The item is authentic.",
        evidence_state="supported",
        caveat="The claim is only supported by synthetic evaluation data.",
    )

    assert package.summary.startswith("Case")
    assert "authentic" not in package.summary.lower()
    assert package.banner == "Decision support. Not a finding of fact."
