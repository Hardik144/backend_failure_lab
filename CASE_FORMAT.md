# Case Format

Every future case should be small, reproducible, and focused on one backend failure mode.

## Case ID Rules

Each case must have a globally unique ID.

Rules:

- ID format: `BFL-0001`.
- `BFL` means `Backend Failure Lab`.
- The ID must not encode the category.
- Do not use category-prefixed IDs such as `SA-0001`, `PS-0001`, or `DB-0001`.
- The ID must not change after publication.
- The folder name should use the format `BFL-0001-short-kebab-case-title`.
- The primary category is stored in `case.yaml`.

Example:

```text
cases/security-auth/BFL-0001-user-can-read-another-users-order/
```

## From Proposal to Case

A case can start as a GitHub issue using the **Failure Case Proposal** template.

Before becoming a full case, it should be checked for:

- clear failure mode;
- realistic production scenario;
- reproducible broken scenario;
- difference from existing cases;
- possible failing test;
- possible fix or pattern.

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
