from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class CitationSource:
    source_id: str
    title: str
    published_at: str  # YYYY-MM-DD or ISO 8601
    quote_span: str
    url: str | None = None


@dataclass(frozen=True)
class TemporalValidationResult:
    is_valid: bool
    as_of_date: str
    valid_sources: tuple[CitationSource, ...]
    invalid_sources: tuple[CitationSource, ...]
    reason: str


class TemporalGuard:
    @staticmethod
    def _parse_date(date_str: str) -> datetime.date:
        clean_str = date_str.strip().split("T")[0]
        return datetime.date.fromisoformat(clean_str)

    @classmethod
    def validate_citations(
        cls,
        as_of_date_str: str,
        sources: Sequence[CitationSource],
    ) -> TemporalValidationResult:
        as_of_date = cls._parse_date(as_of_date_str)
        valid: list[CitationSource] = []
        invalid: list[CitationSource] = []

        for src in sources:
            src_date = cls._parse_date(src.published_at)
            if src_date <= as_of_date:
                valid.append(src)
            else:
                invalid.append(src)

        is_valid = len(invalid) == 0
        if is_valid:
            reason = f"All {len(valid)} citations predate or match the as-of cutoff ({as_of_date_str})."
        else:
            reason = (
                f"Temporal leakage detected: {len(invalid)} citation(s) were published after "
                f"the case as-of cutoff ({as_of_date_str})."
            )

        return TemporalValidationResult(
            is_valid=is_valid,
            as_of_date=as_of_date_str,
            valid_sources=tuple(valid),
            invalid_sources=tuple(invalid),
            reason=reason,
        )
