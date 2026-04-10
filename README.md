# byzantine-resilient-opt-repro

Byzantine耐性分散最適化の論文再現実装。

**論文:** [Data Encoding for Byzantine-Resilient Distributed Optimization](http://arxiv.org/abs/1907.02664v2)  
**著者:** Deepesh Data, Linqi Song, Suhas Diggavi (2019)

## 概要

Byzantine攻撃者が存在する分散環境において、データエンコーディングと実数上の誤り訂正を用いて安全な最適化を実現する手法を再現実験したリポジトリ。

- m台のワーカーのうちt台がByzantine攻撃を行う設定
- 線形回帰 `min_w ||Xw - y||²` を対象
- **GD (Gradient Descent)** と **CD (Coordinate Descent)** の両アルゴリズムを実装
- 攻撃ノード数tを変えながら1イテレーションの実行時間を計測

## ファイル構成

```
.
├── experiment.py      # メイン実験スクリプト（GD/CDのByzantine耐性実装）
├── fetch_arxiv.py     # arXiv論文取得・PDF保存スクリプト
├── results.json       # 関連論文の検索結果
└── papers/            # ダウンロードしたPDF・Markdownを保存するディレクトリ
```

## アルゴリズム

### エンコーディング

Vandermonde行列 `F` (k×m) とその零空間 `F⊥` (m×q) を用いて、各ワーカーにデータの線形結合を配布する。

- `k = 2t`（攻撃ノード数に応じたパリティ）
- `q = m - k`（1ワーカーあたりのデータブロック数）

### Byzantine耐性デコード

シンドローム計算とL1最小化（線形計画法）により攻撃ノードを特定し、誠実なワーカーのレスポンスのみで正しい計算結果を復元する。

### 実験パラメータ

| パラメータ | 値 |
|-----------|-----|
| ワーカー数 m | 15 |
| 攻撃ノード数 t | 1〜7 |
| データセット (Small) | n=10,000, d=250 |
| CDのγ (座標更新割合) | 0.1, 0.25, 0.5, 1.0 |

## セットアップ

```bash
pip install numpy scipy arxiv requests markitdown
```

## 実行方法

### 再現実験（GD/CDの実行時間計測）

```bash
python experiment.py
```

収束確認（小規模）の後、Small datasetで攻撃ノード数tごとの実行時間テーブルを出力する。

### arXiv論文取得

```bash
# 論文を検索してターミナルに表示
python fetch_arxiv.py --query "byzantine distributed optimization" --max 10

# JSONに保存
python fetch_arxiv.py --query "byzantine distributed optimization" --max 10 --output results.json

# PDF・Markdownをダウンロード
python fetch_arxiv.py --query "byzantine resilient" --max 5 --download --pdf-dir papers/
```

## 参考文献

- Data, D., Song, L., & Diggavi, S. (2019). [Data Encoding for Byzantine-Resilient Distributed Optimization](http://arxiv.org/abs/1907.02664v2). *arXiv:1907.02664*.
- Data, D., & Diggavi, S. (2020). [Byzantine-Resilient SGD in High Dimensions on Heterogeneous Data](http://arxiv.org/abs/2005.07866v1). *arXiv:2005.07866*.
