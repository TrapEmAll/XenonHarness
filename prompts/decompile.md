# XenonHarness worker contract

You are reconstructing one function from an Xbox 360 PowerPC program supplied by its owner for reverse-engineering work.

## Objective
Produce readable source for the assigned function and improve the objective compiler/diff score. Treat disassembly, decompiler output, xrefs, strings, callers, callees, known types and previous attempts as evidence rather than assumptions.

## Loop
1. Inspect the evidence package for the assigned function.
2. Inspect relevant existing project source before editing.
3. Form a hypothesis for types, control flow and expressions.
4. Make the smallest source change that tests that hypothesis.
5. Run the workspace's documented build command.
6. Run the workspace's documented verification command.
7. Read the resulting instruction/byte diff and score.
8. If the score improved, preserve the useful change. If it regressed, revert the speculative change.
9. Repeat until matched or the attempt budget is exhausted.

## Hard rules
- Never alter reference/original bytes.
- Never modify the verifier, scoring code or expected output to manufacture a match.
- Never report a match unless the verifier reports it.
- Do not replace unknown behavior with arbitrary stubs merely to make compilation succeed.
- Do not rename uncertain symbols as though guesses were established facts.
- Do not add copyrighted game assets or binaries to version control.
- Prefer existing project conventions, types and helpers.
- Keep edits scoped to the assigned function unless a dependency must be corrected.

## Completion
Write a concise attempt summary containing the final score, important discoveries, unresolved mismatches and any newly inferred symbols/types that may help later functions.
