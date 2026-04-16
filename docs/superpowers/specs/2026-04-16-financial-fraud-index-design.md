# Financial Fraud Index Skill Design

## Goal

Create a standalone agent skill named `financial-fraud-index` that guides an agent to analyze annual reports, identify financial-fraud risk signals, and produce evidence-grounded output without depending on this repository's internal code structure.

## Scope

### In scope

- A release-ready skill package under `skill_release/financial-fraud-index/`
- A self-contained `SKILL.md` with clear trigger conditions and operating rules
- Reusable templates for analysis and report structure
- Example prompts and output outline
- A release checklist for manual validation

### Out of scope

- Packaging this repository itself as an installable agent plugin
- Shipping executable wrappers or repository-specific automation scripts
- Requiring this repository as a runtime dependency

## Packaging Approach

Use a small, documentation-first release package:

```text
skill_release/
  financial-fraud-index/
    SKILL.md
    README.md
    examples/
      example-user-prompts.md
      example-output-outline.md
    templates/
      analysis-checklist.md
      report-outline.md
    checks/
      release-checklist.md
```

This keeps the skill portable while still giving agents enough structure to behave consistently.

## Skill Design

### Trigger conditions

The skill should activate when an agent is asked to:

- analyze an annual report, audit report, or financial statements;
- assess potential accounting manipulation or fraud risk;
- extract evidence-backed red flags from a PDF or extracted report text;
- compare financial-risk findings across companies or reporting periods.

### Core operating rules

The skill must instruct the agent to:

1. identify report type, entity, period, and available source materials;
2. separate confirmed anomalies, weak signals, and missing data;
3. tie conclusions to source excerpts, preferably with page numbers;
4. avoid invented evidence, invented values, or unsupported causal claims;
5. downgrade confidence when evidence or extraction coverage is incomplete.

### Output contract

The skill should make the agent produce:

- a short company/report summary;
- a risk conclusion;
- a signal breakdown;
- evidence excerpts;
- missing-data or pending-review notes when applicable.

## Content Strategy

### `SKILL.md`

Contains the operational workflow, evidence rules, failure modes, and output contract.

### `README.md`

Explains what the skill is, how to install it into an agent skill directory, and how it relates to this repository as a reference implementation.

### Templates and examples

Keep them small and reusable. They should guide future agents, not document the whole project.

## Verification

Manual checks for this release:

- frontmatter is valid and concise;
- skill name uses hyphens only;
- description focuses on when to use, not on the workflow;
- instructions explicitly forbid fabricated evidence;
- package is understandable without reading repository code.

## Success Criteria

- `skill_release/financial-fraud-index/` is self-contained;
- the skill can be copied into another agent environment and still make sense;
- evidence-grounded financial-fraud analysis is the central behavior;
- repository-specific implementation details remain optional reference material.
