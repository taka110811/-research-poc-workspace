# Research Brief

## 1. Theme

- Theme name: timesfm-dhc-demandfc-coldstart-problem
- Short description: 新しい地冷の需要予測において、十分な過去データがないコールドスタート条件でTimesFMがLightGBMより有効か検証する。
- Why now: 既存のLightGBMモデルは数年分の対象地冷データがある場合は運用可能だが、新しい地冷では履歴不足によりそのまま利用しにくい。

## 2. Desired Output

- Final output: PoC設計、実行レポート、継続判断
- Expected reader: 地冷需要予測モデルの開発・運用判断者
- Deadline: TBD
- Format:
  - `poc/design.md`
  - `poc/runs/<date>/report.md`
  - `poc/decision.md`

## 3. Problem

- Problem statement: 新しい地冷では需要実績データが少なく、既存LightGBMモデルが必要とする十分な学習データを確保できない。
- Current pain: 数年分の対象地冷データがないと、従来の教師ありモデルは精度が出にくい。
- Why existing approaches are insufficient: LightGBMは強いベースラインだが、対象地冷固有の十分な履歴データを前提にしやすく、ゼロショットや少量データ条件に弱い可能性がある。

## 4. Target Question

- Main research question: 他の地冷データを用いてTimesFMを活用した場合、ゼロショットまたは少量データ条件の新しい地冷需要予測で、LightGBMベースラインより高い精度を出せるか。
- Sub questions:
  - TimesFMのゼロショット予測は、対象地冷の履歴が短い場合にLightGBMを上回るか。
  - 他地冷データでのファインチューニング、またはLoRAファインチューニングは精度を改善するか。
  - 外生変数を使うLightGBMと、TimesFM単体またはXReg/外生変数付きTimesFMを公平に比較するにはどう設計すべきか。
  - 評価指標 `MAE`, `MAPE`, `MAE / avg_demand` のどれが判断に最も効くか。
- What should be decided after the PoC: TimesFMを本格検証に進めるか、LightGBM改善に集中するか、別の時系列Foundation Modelも比較対象に入れるか。

## 5. Scope

- In scope:
  - 新しい地冷を想定したコールドスタート評価設計
  - LightGBMをベースラインにした精度比較
  - TimesFMゼロショット評価
  - 可能なら他地冷データを使ったTimesFMファインチューニング設計
  - 評価指標: MAE, MAPE, MAE / avg_demand
- Out of scope:
  - 本番導入判断
  - 大規模な全地冷横断の網羅実験
  - データ基盤構築
  - 需要予測以外の制御最適化
- Assumptions:
  - 地冷ごとの需要時系列が存在する。
  - LightGBMの既存実装または同等の再現コードが利用できる。
  - 対象地冷をholdoutし、他地冷を学習・ファインチューニング用に使える。
- Constraints:
  - 可能ならローカルで実行する。
  - PoCは小さく、再現可能な設定にする。
  - コマンド、パラメータ、メトリクス、解釈を記録する。

## 6. Sources

- Seed papers:
  - TimesFM: A decoder-only foundation model for time-series forecasting
- Keywords:
  - TimesFM
  - time series foundation model
  - demand forecasting
  - cold start forecasting
  - district heating and cooling
  - zero-shot forecasting
  - LoRA fine-tuning
- Related systems or libraries:
  - TimesFM
  - LightGBM
  - pandas
  - scikit-learn
- Datasets:
  - 他地冷の需要実績データ
  - 新しい地冷を模したholdout対象地冷データ
  - 気象、曜日、祝日などの外生変数があれば別途検討

## 7. PoC Direction

- Hypothesis: 他地冷データで事前適応したTimesFM、またはTimesFMのゼロショット予測は、対象地冷の履歴が少ない条件でLightGBMより低いMAEまたは低いMAE/avgを出せる可能性がある。
- Minimal implementation:
  - 地冷を1つholdoutする。
  - holdout地冷の履歴長を `0`, `7日`, `30日`, `90日` などに制限する。
  - LightGBMとTimesFMを同じ検証期間で比較する。
  - MAE, MAPE, MAE/avg_demandを出す。
- Baseline:
  - 既存LightGBM
  - LightGBMの少量データ学習
  - 可能なら単純な季節ナイーブ予測
- Metrics:
  - MAE
  - MAPE
  - MAE / avg_demand
- Success criteria:
  - 少なくとも1つのコールドスタート条件でTimesFMがLightGBMを明確に上回る。
  - 評価手順が再現可能で、次の本格検証に必要なデータ要件が明確になる。
  - 結果が地冷運用の意思決定に使える粒度で解釈できる。
- Failure criteria:
  - TimesFMが全条件でLightGBMを下回る。
  - データ形式や依存関係によりローカルPoCが成立しない。
  - 評価設計が不公平で、結果を判断に使えない。

## 8. Execution Environment

- Language: Python
- Runtime: TBD
- Hardware: Local machine if feasible
- External services:
  - Hugging Face model download if TimesFMを使う場合
  - arXiv/GitHub参照
- Reproducibility requirements:
  - 評価対象地冷
  - 学習対象地冷
  - 検証期間
  - 履歴長条件
  - モデル設定
  - 乱数seed
  - 評価指標

## 9. Risks

- Technical risks:
  - TimesFMの依存関係やモデルサイズがローカル実行に重い可能性がある。
  - TimesFMの外生変数対応とLightGBMの特徴量利用条件を公平に比較しにくい。
  - MAPEは需要が小さい時間帯で不安定になる可能性がある。
- Research risks:
  - 他地冷と新地冷の需要パターン差が大きいと転移が効かない可能性がある。
  - ゼロショット性能が公開ベンチマークほど地冷需要に効かない可能性がある。
- Data risks:
  - 地冷ごとのサンプリング周期、欠損、設備差、季節性が揃っていない可能性がある。
  - 対象地冷の「ゼロショット」条件でも検証用の真値データは必要。
- Time risks:
  - ファインチューニングまで含めるとPoCが大きくなりすぎる可能性がある。

## 10. Instruction Text

```text
I want to investigate whether TimesFM can solve the cold-start demand forecasting problem for new district heating and cooling sites.

Final output should be a PoC design, a runnable experiment if data is available, a run report, and a decision memo.

The core question is whether TimesFM, using data from other DHC sites via zero-shot or fine-tuning, can outperform the existing LightGBM baseline when the new DHC site has only a small amount of data or no training history.

Please work backward from a PoC design and execution plan. Define a fair comparison against LightGBM, specify the holdout-site evaluation protocol, define success criteria using MAE, MAPE, and MAE / avg demand, and produce files under topics/timesfm-dhc-demandfc-coldstart-problem/poc/.

Constraints:
- Run locally if feasible.
- Keep the PoC small enough to inspect and reproduce.
- Record commands, parameters, metrics, and interpretation.
- If data is unavailable, produce the PoC design and state exactly what data is needed to run it.

Known sources:
- GitHub Issue #1: https://github.com/taka110811/-research-poc-workspace/issues/1
- TimesFM GitHub: https://github.com/google-research/timesfm
- Google Research blog: https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/

Expected deliverables:
- poc/design.md
- poc/runs/<date>/report.md
- poc/decision.md
```
