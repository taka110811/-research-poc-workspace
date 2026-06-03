# PoC Run Report

## Run Metadata

- Date: 2026-06-03
- Theme: timesfm-dhc-demandfc-coldstart-problem
- Issue: https://github.com/taka110811/-research-poc-workspace/issues/1
- Status: Not executed
- Reason: Required DHC demand data and existing LightGBM baseline artifacts are not present in the repository.

## Requested Action

Create PoC design and run if feasible.

## Feasibility Check

The PoC is not executable yet.

Missing inputs:

- DHC demand time series.
- Target/source site identifiers.
- Existing LightGBM model code, predictions, or reproducible training pipeline.
- Validation period definition.
- Forecast horizon definition.

## Command

No experiment command was run.

```bash
# Pending data and baseline availability
```

## Required Data Contract

Minimum:

```text
timestamp,site_id,demand
```

Preferred:

```text
timestamp,site_id,demand,temperature,humidity,weekday,holiday,hour
```

## Planned Configuration

Initial cold-start settings:

```text
history_days: [0, 7, 30, 90]
baseline: LightGBM
candidate: TimesFM zero-shot
optional_candidate: TimesFM LoRA fine-tuned on source sites
metrics: MAE, MAPE, MAE / avg_demand
```

## Results

No metrics are available yet.

| Metric | Value | Notes |
|---|---:|---|
| MAE | TBD | Requires predictions and ground truth |
| MAPE | TBD | Requires near-zero demand handling rule |
| MAE / avg_demand | TBD | Primary scale-normalized metric |

## Observations

- The issue is well suited to the PoC template because the desired decision is explicit: whether TimesFM should be pursued for new-site cold-start demand forecasting.
- The most important design choice is fairness: LightGBM and TimesFM must be compared with clearly stated data access and feature access.
- A seasonal naive baseline should be added so the result is interpretable even if LightGBM and TimesFM both perform poorly.

## Issues

- No data is currently available in the repository.
- No baseline code or prediction file is currently available.
- Fine-tuning TimesFM may require dependency setup and model download.

## Artifacts

- PoC design: `topics/timesfm-dhc-demandfc-coldstart-problem/poc/design.md`
- Decision memo: `topics/timesfm-dhc-demandfc-coldstart-problem/poc/decision.md`

## Interpretation

The correct next step is not model execution yet. The next step is to prepare a minimal dataset and baseline contract so the first run can be small but fair.

## Next Step

Provide or create:

1. `data/demand.csv` with `timestamp, site_id, demand`.
2. A target holdout site.
3. A validation period.
4. Existing LightGBM predictions or runnable baseline code.
