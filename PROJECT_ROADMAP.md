# Project Roadmap

## Purpose

This document is the living roadmap for `financial-reports-agent`.

Update it whenever one of the following happens:

- a roadmap item is completed;
- a new remediation priority is identified;
- a new feature direction is accepted;
- scope or sequencing changes materially.

## Current Status

### Completed in this pass

- Removed implicit single-file report saving from the analyzer workflow.
- Restored consistency between runtime risk scoring and serialized risk scoring.
- Added turnover ratio calculation for fields already used by downstream rules.
- Made batch analysis honor the requested output format.
- Expanded extractor coverage for sample-report stock code and key liquidity fields.
- Added regression tests for the repaired behaviors.

### Current risks still open

- PDF extraction coverage is narrow and still relies on brittle regex matching.
- Several modeled fields are not extracted yet, especially liquidity and investment-cashflow inputs.
- Runtime thresholds and weights are still largely hard-coded rather than driven by config.
- Logging and error reporting are inconsistent across CLI, core modules, and utilities.
- Batch CLI exposes `--parallel` but does not implement real parallel execution.

## Phase 1: Stability And Trustworthiness

Goal: make outputs defensible and reduce false positives or false negatives caused by incomplete plumbing.

### Priority items

- Expand extractor coverage for `current_assets`, `current_liabilities`, `cash_and_equivalents`, and `net_cash_flow_investing`.
- Build fixture-based tests for representative annual report PDF layouts.
- Wire `configs/thresholds.yaml` and `configs/weights.yaml` into detection and scoring logic.
- Replace mixed `print`/`logging` behavior with a unified logging strategy.
- Clean up packaging and environment setup:
  - align `requirements.txt` with `pyproject.toml`;
  - remove invalid Python-version entries from pip requirements;
  - reduce reliance on `sys.path.insert(...)`.

## Phase 2: Analysis Depth

Goal: improve signal quality and expand the evidence behind each conclusion.

### Priority items

- Add multi-year trend extraction instead of relying mainly on current-year vs prior-year comparisons.
- Introduce industry benchmark loading and peer comparison.
- Strengthen cross-statement consistency checks with explicit reconciliation rules.
- Add evidence traceability so each fraud signal can point back to extracted numbers or note text.
- Distinguish between missing data, weak signal, and confirmed anomaly in report output.

## Phase 3: Productization

Goal: make the project easier to operate, integrate, and scale.

### Priority items

- Define a stable service/API layer on top of the current Python package.
- Implement real batch concurrency and progress reporting.
- Add structured output schemas for downstream systems.
- Improve report rendering options and templates.
- Add environment-aware configuration loading for local/dev/prod use.

## Functional Expansion Directions

These are candidate feature tracks for future releases.

### Data source expansion

- Support structured inputs beyond PDF, such as CSV, Excel, and XBRL-derived data.
- Add hybrid ingestion that combines extracted PDF text with manually supplied corrections.

### Richer fraud analysis

- Governance and auditor-history knowledge base for recurring entity risk.
- Related-party network analysis across multiple reports or issuers.
- Quarter-level seasonality checks, including year-end revenue concentration detection.
- Explicit earnings-quality scoring with factor attribution.

### Analyst workflow

- Review queue for flagged companies.
- Human annotation and override support for extracted fields and risk judgments.
- Report comparison across years and across peers.

### Explainability and auditability

- Per-signal evidence snippets in generated reports.
- Confidence scoring for extracted fields.
- Structured reasoning traces showing how final risk scores were produced.

## Suggested Execution Order

1. Finish Phase 1 data completeness and configuration wiring.
2. Add extractor fixtures and regression coverage before broader rule expansion.
3. Improve explainability together with Phase 2 signal-depth work.
4. Productize only after scoring and extraction reliability improve.
