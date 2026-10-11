import pytest

from backend.credence_gov.mvp import CaseRecord, EvidenceState, G0Decision, MVPChecklist


def test_g0_decision_requires_all_gate_values() -> None:
    ready = G0Decision(
        pilot_owner="state-analyst-team",
        charter_approved=True,
        language_selected="en",
        egress_approved=False,
        key_custody_approved=True,
        retention_approved=True,
        register_available=False,
        workload_defined=True,
    )

    assert ready.is_ready is False

    complete = G0Decision(
        pilot_owner="state-analyst-team",
        charter_approved=True,
        language_selected="en",
        egress_approved=True,
        key_custody_approved=True,
        retention_approved=True,
        register_available=True,
        workload_defined=True,
    )

    assert complete.is_ready is True


def test_case_record_requires_identity_boundary() -> None:
    case = CaseRecord(
        tenant_id="tenant-123",
        owner_id="analyst-456",
        classification="restricted",
        title="Claim review",
    )

    assert case.title == "Claim review"
    assert case.classification == "restricted"

    with pytest.raises(ValueError, match="tenant_id"):
        CaseRecord(
            tenant_id="",
            owner_id="analyst-456",
            classification="restricted",
            title="Bad case",
        )

    with pytest.raises(ValueError, match="owner_id"):
        CaseRecord(
            tenant_id="tenant-123",
            owner_id="",
            classification="restricted",
            title="Bad case",
        )


def test_evidence_state_rejects_real_fake_verdicts() -> None:
    checklist = MVPChecklist(
        g0_decision=G0Decision(
            pilot_owner="state-analyst-team",
            charter_approved=True,
            language_selected="en",
            egress_approved=True,
            key_custody_approved=True,
            retention_approved=True,
            register_available=True,
            workload_defined=True,
        )
    )

    assert EvidenceState.SUPPORTED.value == "supported"
    assert EvidenceState.OUT_OF_SCOPE.value == "out_of_scope"
    assert checklist.requires_human_review("real") is True
    assert checklist.requires_human_review("mixed") is False
