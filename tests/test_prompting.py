from xenonharness.evidence import FunctionEvidence
from xenonharness.prompting import build_prompt


def test_prompt_contains_evidence_and_feedback():
    evidence = FunctionEvidence(
        address=0x82001000,
        name="sub_82001000",
        size=16,
        disassembly="blr",
        decompilation="return;",
        callers=["sub_82000000"],
    )
    prompt = build_prompt("RULES", evidence, "score=75")
    assert "0x82001000" in prompt
    assert "sub_82001000" in prompt
    assert "blr" in prompt
    assert "score=75" in prompt
