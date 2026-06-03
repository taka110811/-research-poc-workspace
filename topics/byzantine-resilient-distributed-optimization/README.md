# Byzantine-Resilient Distributed Optimization

Byzantine耐性分散最適化の論文再現実装。

**論文:** [Data Encoding for Byzantine-Resilient Distributed Optimization](http://arxiv.org/abs/1907.02664v2)  
**著者:** Deepesh Data, Linqi Song, Suhas Diggavi (2019)

## 構成

```text
.
├── research_brief.md      # 調査開始時の入力情報
├── src/
│   └── experiment.py      # GD/CDのByzantine耐性再現実験
├── papers/                # 論文PDF、Markdown、要約、抽出画像
├── notes/                 # 調査メモ
├── poc/                   # PoC設計、実行結果、判断
└── results/               # 検索結果や実験結果
```

## 実行

リポジトリルートから実行する。

```bash
python topics/byzantine-resilient-distributed-optimization/src/experiment.py
```

arXiv検索結果を保存する。

```bash
python scripts/fetch_arxiv.py \
  --query "byzantine distributed optimization" \
  --max 10 \
  --output topics/byzantine-resilient-distributed-optimization/results/arxiv-search-results.json
```

PDFとMarkdownを保存する。

```bash
python scripts/fetch_arxiv.py \
  --query "byzantine resilient" \
  --max 5 \
  --download \
  --pdf-dir topics/byzantine-resilient-distributed-optimization/papers
```

## PoC

- `research_brief.md`: 調査開始時の前提、問い、制約、指示文
- `poc/design.md`: PoC設計
- `poc/runs/<date>/report.md`: 実行レポート
- `poc/decision.md`: 継続・方向転換・停止の判断
