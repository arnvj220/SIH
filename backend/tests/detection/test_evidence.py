from app.detection.evidence import make_evidence


def test_make_evidence_shape():
    e = make_evidence("signer_mismatch", observed="mallory",
                      threshold="alice", rule_id="IMP_01",
                      explanation="Signer mismatch")
    assert e["type"] == "signer_mismatch"
    assert e["rule_id"] == "IMP_01"