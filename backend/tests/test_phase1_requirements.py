from backend.credence_gov.phase1 import Requirement, RequirementCatalog


def test_requirement_catalog_normalizes_ids_and_priorities() -> None:
    catalog = RequirementCatalog(
        [
            Requirement(
                id="FR-001",
                title="Create a case",
                priority="MUST HAVE",
                phase="Phase 1",
                owner="product",
                traceability="§§5.2, 6.3, 13",
            ),
            Requirement(
                id="SEC-006",
                title="Protect secrets",
                priority="MUST HAVE",
                phase="Phase 1",
                owner="security",
                traceability="§§6, 15, 16",
            ),
        ]
    )

    assert catalog.requirements[0].normalized_id == "FR-001"
    assert catalog.requirements[1].normalized_id == "SEC-006"
    assert catalog.priority_rank("MUST HAVE") == 1
    assert catalog.priority_rank("SHOULD HAVE") == 2
    assert catalog.phase_order("Phase 1") == 1


def test_requirement_catalog_orders_must_have_first() -> None:
    catalog = RequirementCatalog(
        [
            Requirement(
                id="NFR-006",
                title="Minimize recurring cost",
                priority="SHOULD HAVE",
                phase="Phase 2",
                owner="ops",
                traceability="§§6, 16, 20, 24",
            ),
            Requirement(
                id="FR-001",
                title="Create a case",
                priority="MUST HAVE",
                phase="Phase 1",
                owner="product",
                traceability="§§5.2, 6.3, 13",
            ),
        ]
    )

    ordered = catalog.order_by_priority_and_phase()
    assert [item.id for item in ordered] == ["FR-001", "NFR-006"]
    assert ordered[0].summary == "FR-001 | MUST HAVE | Phase 1 | Create a case"
