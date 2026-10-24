import json

from xenonharness.evidence import FunctionEvidence


def test_evidence_load_and_render(tmp_path):
    path = tmp_path / "fn.json"
    path.write_text(json.dumps({"address": "0x82000000", "name": "example", "size": 16,
                                "callers": ["caller"], "callees": ["callee"],
                                "disassembly": "blr"}), encoding="utf-8")
    evidence = FunctionEvidence.from_json(path)
    assert evidence.address == 0x82000000
    assert evidence.size == 16
    rendered = evidence.render()
    assert "example" in rendered
    assert "blr" in rendered
