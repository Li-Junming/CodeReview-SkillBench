---
name: evidence-first-code-review
description: Review application code for concrete correctness and reliability defects.
---

# Evidence-first Code Review

Review only the files and task supplied by the caller.

For each potential defect:

1. Identify the exact operation and control flow that creates the failure.
2. Cite the smallest relevant file and line range.
3. Describe a realistic trigger and user-visible impact.
4. Recommend a fix that removes the failure mechanism.
5. Propose a regression test that would fail before the fix.

Prioritize correctness, concurrency, data integrity, security, and error handling.
Do not report style preferences as defects. Do not invent missing infrastructure.
If evidence is insufficient, omit the finding or state the uncertainty explicitly.

Return a JSON object with `summary` and `findings`. Each finding must contain
`id`, `severity`, `title`, `location`, `evidence`, `impact`, `recommendation`,
and `regression_test`.

