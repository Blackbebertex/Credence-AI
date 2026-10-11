import pytest

from backend.credence_gov.bsa_certificate import BSACertificate, BSACertificateGenerator


def test_generate_bsa_certificate_success() -> None:
    artifacts = [
        {"id": "art-01", "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "type": "pdf"},
        {"id": "art-02", "sha256": "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb", "type": "image"},
    ]

    cert = BSACertificateGenerator.generate(
        case_id="case-100",
        deponent_name="Rajesh Kumar",
        deponent_designation="Senior Systems Analyst",
        department="Ministry of Electronics and Information Technology",
        device_identifier="srv-node-credence-01",
        artifacts=artifacts,
        audit_chain_head_hash="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
    )

    assert isinstance(cert, BSACertificate)
    assert cert.case_id == "case-100"
    assert cert.deponent_name == "Rajesh Kumar"
    assert "Section 63" in cert.statutory_reference
    assert "Bharatiya Sakshya Adhiniyam" in cert.statutory_reference
    assert cert.hash_algorithm == "SHA-256"
    assert len(cert.artifact_hashes) == 2
    assert "Decision support. Not a finding of fact." in cert.advisory_notice
    assert len(cert.certificate_hash()) == 64


def test_bsa_certificate_rejects_missing_deponent() -> None:
    with pytest.raises(ValueError, match="deponent_name"):
        BSACertificateGenerator.generate(
            case_id="case-100",
            deponent_name="   ",
            deponent_designation="Analyst",
            department="Dept",
            device_identifier="node",
            artifacts=[],
            audit_chain_head_hash="hash",
        )
