# Financial Reports Agent Critical Remediation Design

## Background

The current project can produce analysis output, but several defects undermine result trustworthiness and operator expectations:

- Single-file analysis saves a Markdown report inside the analyzer and then saves again at the CLI layer, causing duplicate output.
- Batch commands expose a `--format` option that is not propagated to the analysis workflow.
- `RiskAssessment` is scored by `RiskAssessor`, but JSON serialization recalculates the score using a different algorithm, so persisted output can disagree with in-memory output.
- `FinancialStatement` exposes turnover ratios that downstream anomaly and fraud rules rely on, but those ratios are never calculated, leaving rules to operate on default `0.0` values.

This design limits the first remediation pass to correctness and operator-facing consistency. It deliberately avoids a wider extractor/configuration refactor so the project can stabilize in small, testable steps.

## Goal

Fix the highest-impact correctness and workflow issues while establishing a maintained roadmap document for continued project improvement and feature expansion.

## Scope

### In scope

- Remove duplicate save behavior by separating analysis from persistence.
- Make output format selection flow from CLI to save behavior for both single and batch analysis.
- Preserve risk scoring and risk level computed by `RiskAssessor` during serialization.
- Compute the already-modeled turnover ratios needed by existing analysis rules.
- Add regression tests for the repaired behaviors.
- Add a roadmap document that tracks technical improvements and functional expansion directions.

### Out of scope

- Rebuilding the PDF extraction strategy.
- Wiring all YAML configuration into scoring/detection in this pass.
- Replacing all `print` calls with a unified logging subsystem.
- Introducing parallel batch processing implementation for the existing `--parallel` flag.

## Selected Approach

Use a minimal architecture correction rather than a large refactor:

1. Treat `FinancialFraudAnalyzer.analyze()` as a pure analysis orchestrator that returns an `AnalysisReport` without saving files.
2. Extend `FinancialFraudAnalyzer.batch_analyze()` so callers decide output format and whether reports are persisted.
3. Make `RiskAssessment.to_dict()` serialize the already-computed values instead of recomputing them.
4. Compute `inventory_turnover`, `receivables_turnover`, and `total_asset_turnover` in `FinancialStatement.calculate_ratios()` using the same simplified conventions already present in `src/utils/calculation_utils.py`.
5. Add a top-level roadmap document that is intended to be updated as each improvement lands.

This keeps file ownership narrow, minimizes regression risk, and directly addresses the defects already observed in the current codebase.

## File-Level Design

### `src/models/financial_data.py`

- Add turnover ratio calculations to `FinancialStatement.calculate_ratios()`.
- Keep the formulas aligned with existing simplified project conventions:
  - `inventory_turnover = operating_revenue / inventory`
  - `receivables_turnover = operating_revenue / accounts_receivable`
  - `total_asset_turnover = operating_revenue / total_assets`

### `src/models/report_model.py`

- Stop recomputing risk score and level during serialization.
- `RiskAssessment.to_dict()` should serialize the current object state directly.

### `src/core/analyzer.py`

- Remove automatic Markdown save from `analyze()`.
- Add optional batch persistence controls so batch callers can request `markdown` or `json`.
- Keep summary generation behavior intact.

### `main.py`

- Single-file command remains responsible for saving once using the requested format.
- Batch command passes selected format into batch analysis so behavior matches CLI contract.

### `scripts/analyze_fraud.py`

- Continue to save one report in the requested format after `analyze()` returns.

### `scripts/batch_analyze.py`

- Pass `--format` into batch analysis.

### `tests/`

- Add focused regression tests for:
  - turnover ratio calculation;
  - `RiskAssessment.to_dict()` preserving assessor-produced score and level;
  - `analyze()` not saving implicitly;
  - batch analysis saving exactly once per file in the requested format.

### `PROJECT_ROADMAP.md`

- Add a living roadmap at the repo root.
- Include:
  - current system issues;
  - phased remediation plan;
  - feature expansion directions.

## Error Handling

- Existing exception behavior is preserved for this pass.
- Tests should cover behavior at the orchestration layer without requiring real PDF parsing.
- For analyzer workflow tests, use test doubles/stubs to avoid file I/O except for controlled temporary output directories.

## Testing Strategy

- Use pytest regression tests.
- Start with failing tests before implementation.
- Prefer unit-level tests over end-to-end PDF fixtures for this pass.
- Verify:
  - no implicit save from `analyze()`;
  - selected save format is honored in batch mode;
  - serialized risk values remain unchanged;
  - turnover ratios are non-zero when inputs are present.

## Success Criteria

- A single-file analysis run produces one output file, not two.
- Batch analysis respects the requested output format.
- JSON report risk score equals the in-memory score assigned by `RiskAssessor`.
- Existing rules that depend on turnover ratios receive calculated values instead of defaults.
- The repository contains a roadmap document that can be updated alongside future improvements.
