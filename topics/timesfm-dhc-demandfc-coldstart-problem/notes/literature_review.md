# Literature Review: TimesFM for DHC Demand Forecast Cold Start

調査日: 2026-06-03

## 目的

新しい地冷（DHC）の需要予測で、対象地冷の履歴データが少ない、または無いコールドスタート条件を解くために、既存研究・既存モデルからPoCに使えそうなものを整理する。

## 結論

最初のPoCでは、TimesFMだけを検証対象に固定しない方がよい。TimesFMは有力候補だが、エネルギー需要予測の近年研究では、Chronos系、Moirai系、TinyTimeMixer系も比較対象として出ており、単純なSeasonal NaiveやLightGBMが勝つケースも報告されている。

推奨する初期PoC構成:

1. Seasonal Naive
2. 既存LightGBM
3. TimesFM zero-shot
4. Chronos-Bolt or Chronos-2 zero-shot
5. Moirai or TTM zero-shot

その後、TimesFMが有望ならLoRA fine-tuningや外生変数対応を検証する。

## 使えそうな研究・モデル

### 1. TimesFM

候補としては妥当。Google ResearchのTimesFMは、時系列Foundation Modelとしてゼロショット予測を狙ったモデルで、公式GitHubではTimesFM 2.5が最新モデルとして示されている。GitHub READMEには、TimesFM 2.5が長いcontext、量子化予測、LoRA fine-tuning例、XRegによるcovariate supportを持つことが記載されている。

PoCで使える点:

- target地冷の履歴が短い場合のzero-shot候補。
- 他地冷データを使うLoRA fine-tuning候補。
- 気象・カレンダーなどの外生変数を使う場合、XRegの検討余地がある。

注意点:

- LightGBMが外生変数を使う場合、TimesFMをunivariateだけで比較すると不公平。
- fine-tuningは依存関係と実行負荷が増えるため、最初はzero-shotから入るべき。

Sources:

- https://github.com/google-research/timesfm
- https://research.google/blog/a-decoder-only-foundation-model-for-time-series-forecasting/
- https://arxiv.org/abs/2310.10688

### 2. Chronos / Chronos-Bolt / Chronos-2

Chronosは、時系列値をスケーリング・量子化してトークン化し、Transformer系言語モデルとして学習するアプローチ。論文では、多様なデータからの事前学習により、未知データセットでzero-shot性能を出せると報告している。

エネルギー需要予測のzero-shot benchmarkでは、Chronos-BoltやChronos-2が比較対象として使われており、特にChronos-2はcalibration面でも有望という報告がある。

PoCで使える点:

- TimesFMの代替または比較対象。
- zero-shotでまず比較しやすい。
- consumer hardware benchmarkで扱われているため、ローカルPoCの参考になりやすい。

注意点:

- モデル系列・バージョンによって入力形式や確率予測の扱いが異なる。
- LightGBMやTimesFMと同じhorizon・context条件で比較する必要がある。

Sources:

- https://arxiv.org/abs/2403.07815
- https://arxiv.org/abs/2602.10848

### 3. Moirai / Moirai-2 / Moirai-MoE

Moiraiは、universal forecastingを目指す時系列Foundation Model。大規模な時系列アーカイブで事前学習し、zero-shot forecasterとして使う設計。任意変量・複数frequencyへの対応が研究上の特徴。

PoCで使える点:

- multivariateや複数siteを扱う場合の候補。
- TimesFMと異なる設計のFoundation Modelとして比較価値がある。
- エネルギー需要予測の外生変数評価研究でも比較対象に入っている。

注意点:

- エネルギー需要ではFoundation Modelが常に勝つわけではない。
- 外生変数の扱いはモデルごとに異なるため、単純比較しにくい。

Sources:

- https://arxiv.org/abs/2402.02592
- https://arxiv.org/abs/2410.10469
- https://arxiv.org/abs/2602.05390

### 4. TinyTimeMixer / TTM

TTMは軽量なpre-trained modelとして、zero/few-shot forecastingを狙うモデル。エネルギー需要予測や外生変数評価の研究で比較対象に入っている。

PoCで使える点:

- ローカル実行しやすい候補として検討価値がある。
- TimesFMより軽く回せる可能性がある。
- 外生変数やchannel mixingの扱いが需要予測で有利になる可能性がある。

注意点:

- TimesFMを検証したい主目的から外れすぎないよう、初期PoCでは比較候補に留める。

Sources:

- https://huggingface.co/papers/2401.03955
- https://arxiv.org/abs/2602.05390
- https://arxiv.org/abs/2602.10848

## エネルギー需要予測に関する重要な示唆

### 1. Foundation Modelはエネルギー需要で常に勝つわけではない

2026年の電力需要予測benchmarkでは、TSFMはzero-shotで有望だが、精度・calibration・robustnessはモデルと条件に強く依存すると報告されている。別の外生変数評価研究では、Singaporeの安定した気候では単純なbaselineがFoundation Modelを上回るケースもあり、Foundation Model万能論には注意が必要とされている。

PoCへの反映:

- Seasonal Naiveを必ず入れる。
- LightGBMを強いbaselineとして扱う。
- TimesFMだけでなく、Chronos/TTM/Moiraiの少なくとも1つを比較候補にする。
- 「勝てるか」だけでなく「どの履歴長で有利か」を評価する。

Sources:

- https://arxiv.org/abs/2602.10848
- https://arxiv.org/abs/2602.05390

### 2. 外生変数の公平性が重要

電力・熱需要では、気温、曜日、祝日、時刻などの外生変数が効く。LightGBMがこれらを使っている一方で、TimesFMをtarget demandのみで評価すると、TimesFMに不利な比較になる。逆にTimesFMだけ他siteでfine-tuningし、LightGBMにsource-site trainingを許さない場合はTimesFMに有利になる。

PoCへの反映:

- 比較条件を2段階に分ける。
- Univariate条件: すべてのモデルが需要系列のみを使う。
- Exogenous条件: LightGBMとFoundation Model双方で可能な範囲で外生変数を使う。

Sources:

- https://arxiv.org/abs/2602.05390
- https://github.com/google-research/timesfm

## 地冷・熱需要予測の既存研究

### 1. District heating/cooling thermal load forecasting with TFT

District heating/cooling networkのthermal load予測にTemporal Fusion Transformerを使う研究がある。Ulmのdistrict heating networkで8年分のhourly operating dataを使い、72時間先までのload forecastを評価している。

PoCで使える点:

- forecast horizonの候補として72時間が参考になる。
- 地冷/熱需要ではTFTが比較対象になり得る。
- hourly dataと複数grid/siteの設定が今回のholdout-site設計に近い。

Sources:

- https://ecp.ep.liu.se/index.php/sims/article/view/531

### 2. Operational thermal load forecasting with expert advice

District heating networkのthermal load forecastingで、linear regression、extremely randomized trees、feed-forward neural network、SVMなど複数モデルをexpert systemとして組み合わせる研究がある。10棟、27か月、外気温を使って検証している。

PoCで使える点:

- 複数モデルのensembleやbest expert trackingは、LightGBM + TSFMの運用候補として参考になる。
- 外気温情報が重要な入力として扱われている。

Sources:

- https://www.sciencedirect.com/science/article/pii/S0378778817312070

### 3. District heating station transfer learning

District heating stationのthermal load predictionで、cross-year/cross-siteのtransfer learningを評価する研究がある。新しいheating seasonや別siteへの転移で性能低下する問題を扱っており、今回の「新しい地冷」問題に近い。

PoCで使える点:

- 他地冷から新地冷へ転移する評価プロトコルの参考になる。
- multi-source transfer learningの考え方を、TimesFM fine-tuningやLightGBM source-site trainingに反映できる。

Sources:

- https://www.sciencedirect.com/science/article/pii/S0360544221025573

### 4. Building energy transfer learning / few-shot forecasting

建物エネルギー予測では、データが少ないtarget buildingへsource buildingから転移する研究が複数ある。transfer learningで少量履歴でも精度改善を狙う構図は、地冷コールドスタートとかなり近い。

PoCで使える点:

- target履歴長を `7日`, `30日`, `90日` などに切るfew-shot評価が妥当。
- source building/site selectionが精度に効く可能性がある。
- residual correctionやseasonal/trend adjustmentを、LightGBM側の改善案として検討できる。

Sources:

- https://www.sciencedirect.com/science/article/pii/S0360544219324193
- https://www.sciencedirect.com/science/article/pii/S0378778817329171
- https://arxiv.org/abs/2301.10663
- https://arxiv.org/abs/2410.14107

## PoCに取り込むべき具体案

### 案A: Foundation Model比較を先に行う

目的:

- TimesFMだけに賭けず、zero-shotで使えるTSFMを横並びにする。

モデル:

- Seasonal Naive
- LightGBM
- TimesFM
- Chronos-Bolt or Chronos-2
- TTM or Moirai

評価:

- target site holdout
- history days: `0`, `7`, `30`, `90`
- metrics: MAE, MAPE, MAE / avg_demand

優先度: 高

理由:

- 実装が比較的軽く、最初の判断材料になる。
- 既存研究でもTSFMはモデル差が大きい。

### 案B: TimesFM fine-tuningは2段階目にする

目的:

- TimesFM zero-shotが見込みあり、またはzero-shotでは弱いがsource-site adaptationが期待できる場合に進む。

方法:

- source sitesでLoRA fine-tuning。
- target siteはholdout。
- target履歴を少量だけ使うfew-shot settingも評価。

優先度: 中

理由:

- 依存関係・GPU/メモリ・学習設計が増え、初期PoCが重くなる。

### 案C: LightGBM transfer baselineを強化する

目的:

- TimesFMと公平に比較するため、LightGBMにもsource-site情報を使わせる。

方法:

- `source_only`
- `target_limited`
- `source_plus_target`
- `source_plus_target_with_site_id`

優先度: 高

理由:

- TimesFMがsource-site事前知識を使うなら、LightGBMにも同等の情報を与えないと結論が弱い。

### 案D: 外生変数あり/なしを分ける

目的:

- 気温・曜日・祝日・時刻が効く需要予測で、不公平な比較を避ける。

評価条件:

- univariate: `timestamp, site_id, demand`
- exogenous: `temperature, humidity, weekday, holiday, hour` などを追加

優先度: 高

理由:

- 既存研究では外生変数の扱いがTSFM性能に大きく影響する。

## 現時点の推奨

最初の実験は次の構成にする。

```text
target_site: 1つ選ぶ
source_sites: target以外
history_days: [0, 7, 30, 90]
horizon: 24h または 72h
metrics: MAE, MAPE, MAE / avg_demand
models:
  - seasonal_naive
  - lightgbm_target_limited
  - lightgbm_source_plus_target
  - timesfm_zero_shot
  - chronos_or_ttm_zero_shot
```

TimesFM fine-tuningは、zero-shot比較でTimesFMが完全に見込みなしでないことを確認してから進める。

## 次に必要な情報

- 地冷需要データの粒度: hourly / 30min / daily
- 予測horizon: 24h / 48h / 72h / その他
- site数
- 各siteの履歴期間
- 既存LightGBMが使う特徴量
- 既存LightGBMの予測結果を再利用できるか
- 外生変数の有無: 気温、湿度、曜日、祝日、施設稼働情報
- MAPEでゼロ需要・低需要をどう扱うか
