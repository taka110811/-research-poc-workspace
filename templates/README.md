# Templates

研究テーマをPoCアウトプットから逆算して進めるためのテンプレート。

## Files

- `research_brief.md`: 調査開始前に埋める入力シート。調査依頼や作業指示に貼る文章まで整理する。
- `poc/design.md`: PoC設計。問い、仮説、成功条件、実行計画を書く。
- `poc/run_report.md`: PoC実行結果。コマンド、設定、メトリクス、解釈を書く。
- `poc/decision.md`: PoC後の判断。継続、方向転換、停止を決める。

## Workflow

1. `topics/<theme-name>/` を作る。
2. `templates/research_brief.md` を `topics/<theme-name>/research_brief.md` として用意し、調査開始情報を埋める。
3. `templates/poc/design.md` と `templates/poc/decision.md` を `topics/<theme-name>/poc/` に用意する。
4. PoC実行ごとに `templates/poc/run_report.md` を `topics/<theme-name>/poc/runs/<date>/report.md` として用意する。
5. 実行結果をもとに `poc/decision.md` を更新する。

## GitHub Issue

スマホから依頼する場合は `.github/ISSUE_TEMPLATE/research-poc.yml` の `Research PoC Request` を使う。

Issueの内容は、まず `research_brief.md` に整理し、その後 `poc/design.md`、`poc/runs/<date>/report.md`、`poc/decision.md` へ展開する。
