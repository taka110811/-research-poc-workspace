# PoC Decision

## Summary

Issue #1 has been converted into a PoC design. The PoC has not been executed because the repository does not yet contain DHC demand data or the existing LightGBM baseline.

## Decision

- Continue / Pivot / Stop: Continue
- Reason: The research question is concrete, the baseline is known, and the metrics are defined. Execution is blocked only by missing data and baseline artifacts, not by unclear scope.

## Evidence

- Existing baseline: LightGBM
- Candidate model: TimesFM
- Target setting: new DHC cold-start forecasting
- Metrics: MAE, MAPE, MAE / avg_demand
- Missing execution inputs are explicit in `poc/runs/2026-06-03/report.md`.

## What Worked

- The issue template captured the core question and baseline.
- The PoC can be framed as a holdout-site evaluation.
- The success and failure conditions can be made measurable.

## What Did Not Work

- The PoC could not be run without DHC demand data.
- The existing LightGBM implementation or prediction artifacts are not in the repository.
- TimesFM dependency setup has not been tested locally.

## Follow-up Work

- Add a minimal `data/demand.csv` or document where the private data should be mounted.
- Add or reference the existing LightGBM baseline.
- Implement a small evaluation script that computes MAE, MAPE, and MAE / avg_demand.
- Run TimesFM zero-shot before attempting fine-tuning.
- Add TimesFM fine-tuning only after the zero-shot baseline is measured.

## Open Questions

- What is the demand sampling interval: hourly, 30-minute, daily, or another frequency?
- What forecast horizon matters operationally?
- Which site should be treated as the new target site?
- Are weather and calendar features available?
- Should the first PoC compare univariate forecasts only, or include exogenous variables for both LightGBM and TimesFM?
