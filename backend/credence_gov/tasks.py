from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any


class TaskQueueName(str, Enum):
    P0_DEADLINE = "p0_deadline"
    P1_ELEVATED = "p1_elevated"
    P2_ROUTINE = "p2_routine"
    P3_BULK = "p3_bulk"


class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class AnalysisTaskResult:
    task_id: str
    case_id: str
    artifact_id: str
    queue: TaskQueueName
    status: JobStatus
    evidence_state: str
    extracted_text: str | None
    error_message: str | None = None


class PlaceholderAnalysisWorker:
    """Placeholder text extraction; this implementation is not sandboxed or an analyzer."""

    @classmethod
    def execute_analysis(
        cls,
        *,
        task_id: str,
        case_id: str,
        artifact_id: str,
        raw_bytes: bytes,
        mime_type: str,
        queue: TaskQueueName = TaskQueueName.P2_ROUTINE,
        simulate_failure: bool = False,
    ) -> AnalysisTaskResult:
        if simulate_failure:
            # PR-07: Fail closed => insufficient_evidence + mandatory review
            return AnalysisTaskResult(
                task_id=task_id,
                case_id=case_id,
                artifact_id=artifact_id,
                queue=queue,
                status=JobStatus.FAILED,
                evidence_state="insufficient_evidence",
                extracted_text=None,
                error_message="Worker timeout or sandbox error encountered. Fail-closed engaged.",
            )

        if not raw_bytes:
            return AnalysisTaskResult(
                task_id=task_id,
                case_id=case_id,
                artifact_id=artifact_id,
                queue=queue,
                status=JobStatus.FAILED,
                evidence_state="insufficient_evidence",
                extracted_text=None,
                error_message="Zero-byte payload.",
            )

        # Decode only as a convenience for synthetic fixtures. Text presence is
        # not evidence and must never produce a supportive finding by itself.
        decoded_text = raw_bytes.decode("utf-8", errors="replace").strip()
        return AnalysisTaskResult(
            task_id=task_id,
            case_id=case_id,
            artifact_id=artifact_id,
            queue=queue,
            status=JobStatus.COMPLETED,
            evidence_state="insufficient_evidence",
            extracted_text=decoded_text,
            error_message=None,
        )


# Keep the previous import name for callers, but document that no sandbox is
# provided by this placeholder implementation.
SandboxedAnalysisWorker = PlaceholderAnalysisWorker


class TaskDispatcher:
    def __init__(self) -> None:
        self._dispatched: dict[str, AnalysisTaskResult] = {}

    def enqueue_analysis_job(
        self,
        *,
        case_id: str,
        artifact_id: str,
        raw_bytes: bytes,
        mime_type: str,
        queue: TaskQueueName = TaskQueueName.P2_ROUTINE,
        simulate_failure: bool = False,
    ) -> AnalysisTaskResult:
        task_id = f"task-{uuid.uuid4().hex[:10]}"
        result = PlaceholderAnalysisWorker.execute_analysis(
            task_id=task_id,
            case_id=case_id,
            artifact_id=artifact_id,
            raw_bytes=raw_bytes,
            mime_type=mime_type,
            queue=queue,
            simulate_failure=simulate_failure,
        )
        self._dispatched[task_id] = result
        return result
