# Case Format

Every future case should be small, reproducible, and focused on one backend failure mode.

## Required Sections

### Title

A short, specific name for the failure case.

### Category

The primary category from [TAGS.md](TAGS.md).

### Level

The expected reader level from [TAGS.md](TAGS.md).

### Stack

The main technologies involved in the case.

### Problem

What is broken and why the failure matters.

### Why This Happens in Production

The real-world conditions that make the issue likely.

### Broken Scenario

The user-facing or system-facing behavior that demonstrates the bug.

### Broken Implementation

The intentionally broken code used for the exercise.

### Failing Test

A test that reproduces the failure clearly.

### Diagnosis

The reasoning process used to identify the root cause.

### Fixed Implementation

The corrected code.

### Production Notes

Operational notes, monitoring hints, deployment concerns, and follow-up checks.

### Trade-Offs

What the fix improves and what costs or limitations it introduces.

### Possible Extensions

Ideas for making the case deeper without expanding the core exercise.

### Evidence of Demand

Why this failure mode is worth teaching.

### Scalability

How the issue or fix changes under higher traffic, larger data volume, or distributed execution.
