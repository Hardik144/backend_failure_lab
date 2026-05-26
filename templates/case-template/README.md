# Case Title

## Summary

Briefly describe the failure scenario and why it matters.

## What You Will Learn

- The failure mode demonstrated by this case.
- How to reproduce the issue with a failing test.
- How to reason from symptoms to root cause.
- How to apply and evaluate the fix.

## Run Broken Version

```bash
pytest
```

## Run Fixed Version

```bash
pytest
```

## Expected Failure

Describe the failing behavior and the expected test output.

## Expected Fix

Describe what changes after the fix is applied.

## Files

- `case.yaml` - case metadata
- `problem.md` - problem statement
- `diagnosis.md` - root cause analysis
- `production-notes.md` - production guidance
- `tradeoffs.md` - trade-offs and limitations
- `broken/` - intentionally broken implementation
- `fixed/` - corrected implementation
- `tests/` - tests that reproduce and verify the behavior

## Related Concepts

List related tags, patterns, and production concepts.
