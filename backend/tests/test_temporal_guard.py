import pytest

from backend.credence_gov.temporal_guard import CitationSource, TemporalGuard


def test_temporal_guard_accepts_valid_prior_sources() -> None:
    sources = [
        CitationSource(
            source_id="src-01",
            title="Official Gazette Notification",
            published_at="2026-09-15",
            quote_span="Section 4 mandates electronic evidence verification",
        ),
        CitationSource(
            source_id="src-02",
            title="Department Circular",
            published_at="2026-10-01",
            quote_span="Effective immediately from October 1st",
        ),
    ]

    result = TemporalGuard.validate_citations("2026-10-01", sources)
    assert result.is_valid is True
    assert len(result.valid_sources) == 2
    assert len(result.invalid_sources) == 0
    assert "All 2 citations predate" in result.reason


def test_temporal_guard_detects_post_dated_leakage() -> None:
    sources = [
        CitationSource(
            source_id="src-01",
            title="Historical Notification",
            published_at="2026-09-01",
            quote_span="Historical rules apply",
        ),
        CitationSource(
            source_id="src-leak",
            title="Future Press Release",
            published_at="2026-10-15T10:00:00Z",
            quote_span="New retrospective interpretation",
        ),
    ]

    result = TemporalGuard.validate_citations("2026-10-01", sources)
    assert result.is_valid is False
    assert len(result.valid_sources) == 1
    assert len(result.invalid_sources) == 1
    assert result.invalid_sources[0].source_id == "src-leak"
    assert "Temporal leakage detected" in result.reason
