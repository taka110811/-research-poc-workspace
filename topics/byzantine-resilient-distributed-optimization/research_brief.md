# Research Brief

## 1. Theme

- Theme name: Byzantine-Resilient Distributed Optimization
- Short description: Byzantine攻撃者がいる分散環境で、データエンコーディングと誤り訂正により安全に最適化する手法を検証する。
- Why now: 分散学習や外部ワーカー利用時の信頼性・耐攻撃性を、PoCとして実装可能な粒度で評価したい。

## 2. Desired Output

- Final output: PoC設計、実装、実行結果、継続判断
- Expected reader: 研究・開発判断をする自分、または実装担当者
- Deadline: TBD
- Format: `poc/design.md`, `poc/runs/<date>/report.md`, `poc/decision.md`

## 3. Problem

- Problem statement: 分散最適化で一部ワーカーが任意に誤った値を返すと、通常の勾配計算や座標更新が破壊される。
- Current pain: Byzantine耐性手法は理論が重く、どの程度実装・検証可能か見えにくい。
- Why existing approaches are insufficient: 単純な多数決やロバスト集約だけでは、論文が主張する確定的保証や誤り訂正ベースの特性を再現できない。

## 4. Target Question

- Main research question: データエンコーディングによるByzantine耐性分散最適化を、小規模PoCで再現し、攻撃ノード数に対する復元性と実行時間を確認できるか。
- Sub questions:
  - GDとCDでPoCとして測るべき最小メトリクスは何か。
  - 攻撃ノード数 `t` を変えたとき、復元成功率と実行時間はどう変化するか。
  - 実装コストに対して、継続調査する価値があるか。
- What should be decided after the PoC: 継続して実装精度を上げるか、別のByzantine耐性手法と比較するか、調査を止めるか。

## 5. Scope

- In scope:
  - 合成データによる線形回帰
  - GD/CDの1イテレーション実行時間
  - Byzantine攻撃ノードのノイズ注入
  - 復元・デコード処理の確認
- Out of scope:
  - 大規模実データセット
  - 本番分散システム
  - 厳密な論文完全再現
  - セキュリティ脅威モデル全般
- Assumptions:
  - PythonでPoC実装する。
  - ワーカーはプロセスやマシンではなく、配列計算としてシミュレーションする。
- Constraints:
  - ローカル環境で実行できるサイズにする。
  - 結果は再実行可能なコマンドと設定で残す。

## 6. Sources

- Seed papers:
  - Data, Song, Diggavi (2019), Data Encoding for Byzantine-Resilient Distributed Optimization
- Keywords:
  - Byzantine resilient distributed optimization
  - data encoding
  - real-number error correction
  - gradient descent
  - coordinate descent
- Related systems or libraries:
  - NumPy
  - SciPy
- Datasets:
  - 合成線形回帰データ

## 7. PoC Direction

- Hypothesis: 小規模合成データであれば、攻撃ノードを混ぜてもデコードにより正しい行列ベクトル積を復元でき、攻撃数増加に伴う実行時間の増加を観測できる。
- Minimal implementation: 既存の `src/experiment.py` をベースに、実行設定・ログ・メトリクスをPoCレポートへ落とす。
- Baseline: Byzantine攻撃なし、または通常のGD/CD。
- Metrics:
  - 1イテレーション実行時間
  - master time
  - worker time
  - 復元誤差
  - 攻撃ノード数 `t`
- Success criteria:
  - 小規模設定でスクリプトが再現可能に動く。
  - `t` ごとの結果が表で残る。
  - 継続・停止判断に使えるレポートが書ける。
- Failure criteria:
  - デコードが不安定で結果を解釈できない。
  - 実行時間がローカルPoCとして扱えないほど重い。

## 8. Execution Environment

- Language: Python
- Runtime: TBD
- Hardware: Local machine
- External services: arXiv取得時のみネットワーク
- Reproducibility requirements: 実行コマンド、乱数seed、データサイズ、依存ライブラリを記録する。

## 9. Risks

- Technical risks:
  - 数値安定性によりデコードが失敗する可能性がある。
  - 論文の符号化方式を簡略化しすぎる可能性がある。
- Research risks:
  - PoC結果が論文主張の本質を十分に検証しない可能性がある。
- Data risks:
  - 合成データだけでは実用性判断が弱い。
- Time risks:
  - 大きいデータサイズでは実行時間が伸びる。

## 10. Instruction Text

```text
I want to investigate Byzantine-Resilient Distributed Optimization.

Final output should be a PoC design, runnable experiment, run report, and decision memo.

The core question is whether data encoding and real-number error correction can be reproduced in a small local PoC to tolerate Byzantine worker responses during distributed optimization.

Please work backward from a PoC design and execution plan. Summarize the relevant papers, identify what must be implemented, define success criteria, propose a minimal PoC, run the experiment if feasible, and produce files under topics/byzantine-resilient-distributed-optimization/poc/.

Constraints:
- Use local Python implementation.
- Keep the experiment small enough to run locally.
- Record commands, parameters, metrics, and interpretation.

Known sources:
- Data, Song, Diggavi (2019), Data Encoding for Byzantine-Resilient Distributed Optimization
- topics/byzantine-resilient-distributed-optimization/papers/1907.02664v2_summary.md

Expected deliverables:
- poc/design.md
- poc/runs/<date>/report.md
- poc/decision.md
```
