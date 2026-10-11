import pytest

from backend.credence_gov.tasks import (
    JobStatus,
    SandboxedAnalysisWorker,
    TaskDispatcher,
    TaskQueueName,
)


def test_sandboxed_worker_executes_analysis() -> None:
    dispatcher = TaskDispatcher()
    payload = b"Extracted Claim: Government announces flood relief."

    result = dispatcher.enqueue_analysis_job(
        case_id="case-flood-01",
        artifact_id="art-doc-01",
        raw_bytes=payload,
        mime_type="text/plain",
        queue=TaskQueueName.P1_ELEVATED,
    )

    assert result.status == JobStatus.COMPLETED
    assert result.queue == TaskQueueName.P1_ELEVATED
    assert result.evidence_state == "insufficient_evidence"
    assert "Government announces flood relief" in result.extracted_text
    assert result.error_message is None


def test_sandboxed_worker_fail_closed_on_error() -> None:
    dispatcher = TaskDispatcher()

    # Simulate timeout / sandbox crash
    result = dispatcher.enqueue_analysis_job(
        case_id="case-timeout-01",
        artifact_id="art-crash-01",
        raw_bytes=b"Untrusted Payload",
        mime_type="application/octet-stream",
        queue=TaskQueueName.P0_DEADLINE,
        simulate_failure=True,
    )

    # PR-07: Fail closed => insufficient_evidence + mandatory human review
    assert result.status == JobStatus.FAILED
    assert result.evidence_state == "insufficient_evidence"
    assert result.extracted_text is None
    assert "Fail-closed engaged" in result.error_message
