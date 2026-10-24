import json

from xenonharness.verification import CommandVerifier


def test_verifier_parses_score(tmp_path):
    result = tmp_path / "result.json"
    result.write_text(json.dumps({"score": 99.5, "summary": "close"}), encoding="utf-8")
    verifier = CommandVerifier(tmp_path, "python -c pass", "python -c pass", result)
    verified = verifier.verify(0x82000000)
    assert verified.score == 99.5
    assert not verified.matched
    assert verified.summary == "close"
