# PoC Design

## Goal

Evaluate whether TimesFM can improve demand forecasting for a new district heating and cooling site under cold-start conditions where the target site has little or no training history.

The first PoC should not assume TimesFM is the only useful candidate. Recent energy-load forecasting studies report strong model and feature-condition dependence, so at least one additional time-series foundation model should be evaluated alongside TimesFM.

## Research Question

Can TimesFM, used zero-shot or adapted with data from other DHC sites, outperform the existing LightGBM baseline for a new DHC site's demand forecast?

## Hypothesis

TimesFM may provide a stronger prior than a target-site-only LightGBM model when target history is scarce. The advantage should be most visible in `0`, `7-day`, `30-day`, or `90-day` history conditions. LightGBM may remain stronger when enough target-site history and external features are available.

## Background

TimesFM is a Google Research time-series foundation model for forecasting. Google describes it as pretrained on a large corpus of time-series data and designed for zero-shot forecasting across domains. The current open TimesFM repository lists TimesFM 2.5 as the latest model version and includes LoRA fine-tuning examples through Hugging Face Transformers and PEFT.

For this PoC, the important implication is not that TimesFM will automatically beat LightGBM, but that it is a plausible cold-start baseline because it can forecast from limited context and may benefit from cross-site adaptation.

## Scope

### In Scope

- One or more DHC sites used as source sites.
- One DHC site held out as the target cold-start site.
- LightGBM baseline comparison.
- TimesFM zero-shot evaluation.
- At least one additional time-series foundation model comparison, such as Chronos-Bolt, Chronos-2, Moirai, or TinyTimeMixer.
- Optional TimesFM fine-tuning or LoRA adaptation if feasible.
- Metrics: MAE, MAPE, MAE / avg_demand.

### Out of Scope

- Production deployment.
- Full hyperparameter tuning.
- Full-scale multi-site benchmarking.
- Control optimization or operational scheduling.
- Final business decision.

## Success Criteria

- A reproducible holdout-site evaluation protocol is defined.
- The same forecast horizon and validation period are used for LightGBM and TimesFM.
- Metrics are calculated for each cold-start condition.
- TimesFM beats LightGBM on at least one practically relevant cold-start condition, or the PoC clearly explains why it does not.
- The decision memo can state Continue, Pivot, or Stop.

## Failure Criteria

- Required DHC data is unavailable.
- Data format cannot be normalized into a consistent timestamp-demand schema.
- TimesFM cannot run locally or through an acceptable runtime.
- LightGBM and TimesFM are compared under unfair feature or data conditions.
- MAPE is dominated by near-zero demand periods and cannot be interpreted.

## Baseline

Primary baseline:

- Existing LightGBM model.

Secondary baseline, recommended for interpretability:

- Seasonal naive forecast, such as previous day or previous week same time.

The seasonal naive baseline helps identify whether TimesFM and LightGBM are both clearing a minimal operational bar.

## Method

### Dataset Layout

Prepare one normalized table:

```text
timestamp, site_id, demand
```

Optional external variables:

```text
timestamp, site_id, demand, temperature, humidity, weekday, holiday, hour
```

### Holdout Protocol

1. Select one target site as the simulated new DHC site.
2. Use all other sites as source sites.
3. Define a fixed validation period for the target site.
4. For the target site, expose only limited history before validation:
   - `0` days: zero-shot or no target training history.
   - `7` days.
   - `30` days.
   - `90` days.
5. Compare all models on the same validation timestamps.

### Model Conditions

Minimum PoC:

- `lightgbm_target_limited`: LightGBM trained only on available target-site history.
- `timesfm_zero_shot`: TimesFM forecast using available target context.
- `chronos_or_ttm_zero_shot`: one additional TSFM zero-shot candidate to check whether TimesFM is uniquely promising.
- `seasonal_naive`: previous day or previous week same time.

Extended PoC:

- `lightgbm_source_plus_target`: LightGBM trained on source sites plus limited target-site history, with `site_id` or site embeddings if available.
- `timesfm_lora_source`: TimesFM fine-tuned or LoRA-adapted on source sites.
- `timesfm_xreg`: TimesFM with covariate support if weather and calendar variables are available and setup is feasible.
- `moirai_or_ttm_exogenous`: a multivariate or covariate-capable TSFM if external features are central to the existing LightGBM baseline.

### Forecast Horizon

Use the operationally relevant forecast horizon. If not yet fixed, start with:

- 24 hours ahead for hourly demand.
- 48 hours ahead if operations require next-day planning.

### Metrics

For validation timestamps `t = 1..N`:

```text
MAE = mean(abs(y_t - yhat_t))
MAPE = mean(abs((y_t - yhat_t) / y_t)) * 100
MAE / avg_demand = MAE / mean(y_t)
```

MAPE should either exclude near-zero demand timestamps or use an epsilon guard. The report must state which rule was used.

## Inputs

- GitHub Issue #1:
  - `https://github.com/taka110811/-research-poc-workspace/issues/1`
- Literature review:
  - `notes/literature_review.md`
- TimesFM sources:
  - `https://github.com/google-research/timesfm`
  - `https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/`
- DHC data needed:
  - Site identifier.
  - Timestamp.
  - Demand value.
  - Optional weather and calendar features.
  - Existing LightGBM prediction or reproducible LightGBM training code.

## Outputs

- `results/metrics.csv`
- `results/predictions.csv`
- `poc/runs/<date>/report.md`
- `poc/decision.md`

Recommended metrics table:

```text
site_id, history_days, model, horizon, mae, mape, mae_over_avg, notes
```

## Execution Plan

1. Confirm available DHC data and LightGBM baseline artifacts.
2. Normalize data to `timestamp, site_id, demand`.
3. Define target holdout site and validation period.
4. Implement seasonal naive baseline.
5. Reproduce or call existing LightGBM baseline.
6. Run TimesFM zero-shot for the same target windows.
7. Run at least one additional TSFM zero-shot candidate, preferably Chronos-Bolt/Chronos-2 or TinyTimeMixer.
8. If feasible, run source-site TimesFM LoRA fine-tuning.
9. Calculate MAE, MAPE, MAE / avg_demand.
10. Write run report and decision memo.

## Required Data Before Running

This PoC cannot be executed yet because the repository does not contain DHC demand data or the existing LightGBM baseline code/artifacts.

Minimum required files:

```text
topics/timesfm-dhc-demandfc-coldstart-problem/data/demand.csv
topics/timesfm-dhc-demandfc-coldstart-problem/src/lightgbm_baseline.py
```

Minimum `demand.csv` columns:

```text
timestamp,site_id,demand
```

Preferred additional columns:

```text
temperature,humidity,weekday,holiday,hour
```

## Risks

- If LightGBM uses rich weather/calendar features and TimesFM is run univariate, the comparison may unfairly favor LightGBM.
- If TimesFM is fine-tuned on source sites but LightGBM is not allowed source-site training, the comparison may unfairly favor TimesFM.
- MAPE may be misleading if demand approaches zero.
- Target-site selection may dominate results; at least two holdout sites are preferable after the first PoC.
- Foundation models may not beat simple or LightGBM baselines in stable demand/climate conditions, so the PoC must include simple baselines and clear failure criteria.

## Decision Rule

Continue if TimesFM zero-shot or source-site adaptation improves `MAE / avg_demand` over LightGBM in low-history settings, or if it is close enough while requiring much less target-site data.

Pivot if TimesFM underperforms but reveals a useful source-site transfer protocol that can improve LightGBM.

Stop if TimesFM cannot run practically, cannot use the available data shape, or consistently underperforms simple baselines.
