# research

複数の研究テーマをまとめるためのワークスペース。

各テーマは `topics/<theme-name>/` 配下にまとめ、テーマごとにコード、論文、実験結果を分けて管理する。

## ディレクトリ構成

```text
.
├── scripts/            # 複数テーマで使う共通スクリプト
├── templates/          # 調査開始・PoC設計のテンプレート
├── topics/
│   └── byzantine-resilient-distributed-optimization/
│       ├── src/        # テーマ固有の実験スクリプト
│       ├── papers/     # 論文PDF、Markdown、要約、図
│       ├── notes/      # 調査メモ
│       ├── poc/        # PoC設計、実行結果、判断
│       └── results/    # 検索結果や実験結果
└── README.md
```

## 研究テーマ

### Byzantine-Resilient Distributed Optimization

Byzantine耐性分散最適化の論文再現実装。

**論文:** [Data Encoding for Byzantine-Resilient Distributed Optimization](http://arxiv.org/abs/1907.02664v2)  
**著者:** Deepesh Data, Linqi Song, Suhas Diggavi (2019)

対象:

- m台のワーカーのうちt台がByzantine攻撃を行う設定
- 線形回帰 `min_w ||Xw - y||^2`
- GD (Gradient Descent) と CD (Coordinate Descent)
- 攻撃ノード数tを変えた1イテレーション実行時間の計測

主要ファイル:

```text
topics/byzantine-resilient-distributed-optimization/
├── research_brief.md
├── src/
│   └── experiment.py
├── papers/
│   ├── 1907.02664v2.pdf
│   ├── 1907.02664v2.md
│   ├── 1907.02664v2_docling.md
│   ├── 1907.02664v2_summary.md
│   └── 1907.02664v2_images/
├── poc/
│   ├── design.md
│   ├── runs/
│   └── decision.md
└── results/
    └── arxiv-search-results.json
```

## セットアップ

```bash
pip install numpy scipy arxiv requests markitdown
```

## 実行方法

### 再現実験

```bash
python topics/byzantine-resilient-distributed-optimization/src/experiment.py
```

### arXiv論文取得

```bash
python scripts/fetch_arxiv.py \
  --query "byzantine distributed optimization" \
  --max 10
```

JSON保存:

```bash
python scripts/fetch_arxiv.py \
  --query "byzantine distributed optimization" \
  --max 10 \
  --output topics/byzantine-resilient-distributed-optimization/results/arxiv-search-results.json
```

PDF・Markdown保存:

```bash
python scripts/fetch_arxiv.py \
  --query "byzantine resilient" \
  --max 5 \
  --download \
  --pdf-dir topics/byzantine-resilient-distributed-optimization/papers
```

## テーマ追加時の方針

新しい研究テーマは次の形で追加する。

```text
topics/<theme-name>/
├── research_brief.md
├── src/        # テーマ固有の実装、実験、分析スクリプト
├── papers/     # 論文、要約、図表
├── notes/      # 調査メモ
├── poc/        # PoC設計、実行結果、判断
│   ├── design.md
│   ├── runs/
│   └── decision.md
├── results/    # 実験結果、検索結果、ログ
└── README.md   # テーマ固有のメモを増やす場合
```

複数テーマで使える処理は `scripts/` に置く。テーマ固有の再現実験や分析コードだけを `topics/<theme-name>/src/` に置く。

## 調査開始時の入力

新しいテーマを始めるときは、まず `templates/research_brief.md` をテーマ配下へコピーして埋める。

特に埋めるべき項目:

- `Desired Output`: 最終的に欲しい成果物
- `Target Question`: PoCで答える問い
- `Scope`: やること、やらないこと
- `Sources`: 起点になる論文、キーワード、データセット
- `PoC Direction`: 仮説、最小実装、評価指標、成功条件
- `Instruction Text`: 調査依頼や作業指示にそのまま貼る文章

PoC成果物は次の3つを基本にする。

- `poc/design.md`: 何を検証するか、どう成功判定するか
- `poc/runs/<date>/report.md`: 実行コマンド、設定、結果、解釈
- `poc/decision.md`: 継続、方向転換、停止の判断

## GitHub Issueからの依頼

スマホから調査指示を出す場合は、GitHub Issueの `Research PoC Request` テンプレートを使う。

Issueに書く最小項目:

- `Theme name`: テーマ名
- `Short description`: 何を調べるか
- `Desired output`: 欲しい成果物
- `Core question`: PoCで答える問い
- `Seed sources`: 起点になる論文、URL、キーワード
- `PoC direction`: 仮説、最小実装、評価指標、成功条件
- `Requested action`: Codexに最初にしてほしい作業

CodexにIssue処理を依頼するときの例:

```text
GitHub Issue #<number> の Research PoC Request を読んで、
research_brief.md と poc/design.md に落とし込んでください。
実行可能ならPoCも走らせて、poc/runs/<date>/report.md と poc/decision.md まで作成してください。
```
