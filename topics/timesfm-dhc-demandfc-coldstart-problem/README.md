# TimesFM DHC Demand Forecast Cold Start Problem

新しい地冷（地域冷暖房）の需要予測におけるコールドスタート問題を、TimesFMで改善できるか検証するPoC。

## Context

既存のLightGBMモデルは運用可能な精度まで構築済みだが、数年分の対象地冷データがないと精度が悪くなりやすい。新しい地冷では十分な履歴データがないため、他地冷データでTimesFMを活用し、ゼロショットまたは少量データで従来手法を上回れるかを検証する。

## Structure

```text
.
├── research_brief.md
├── src/
├── papers/
├── notes/
├── poc/
│   ├── design.md
│   ├── runs/
│   │   └── 2026-06-03/
│   │       └── report.md
│   └── decision.md
└── results/
```

## PoC Outputs

- `research_brief.md`: Issue #1から整理した調査開始情報
- `poc/design.md`: PoC設計
- `poc/runs/2026-06-03/report.md`: 初期実行可否レポート
- `poc/decision.md`: 現時点の判断と次アクション

## Seed Sources

- GitHub Issue #1: https://github.com/taka110811/-research-poc-workspace/issues/1
- TimesFM GitHub: https://github.com/google-research/timesfm
- Google Research blog: https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/
