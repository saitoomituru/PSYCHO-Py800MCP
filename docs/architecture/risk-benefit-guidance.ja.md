# Risk × Benefit ガイダンスと音声合成

状態: `[DESIGNED]` `[PROVISIONAL]`

## 1. 目的

`ExecutionRiskScore`と`EvidenceValueScore`を、技術非専門者が一読して次の会話へ進める日本語へ戻す。
数字は注意を引く圧縮表示、文章は意味と推奨行動を伝える表示とする。

主対象は、定格や波形から危険を察知するDev／Engineerではなく、予算、人員、停止損失、品質投資、
project継続を決める非技術の決裁層である。技術用語を薄めるのでなく、根拠へのlinkを保ったまま
capital、schedule、quality、option valueへ翻訳する。

本ガイダンスは安全ゲート、MeasurementPlan承認、法的責任判定ではない。

二つのscoreは`scale_kind=ordinal_metaphor`の会話用メタ表記である。1点差、比率、積に定量的意味はなく、
円、確率、事故率、損害額、ROI、企業価値へ換算しない。

## 2. スコアの意味

### ExecutionRiskScore

提案された執行の物理risk、影響の重さ、unknown、必要checkをプレゼンテーション用に並べた順序値。
ユーザー成立済み観測をAIが読むだけなら、その読取行為自体はriskへ加算しない。

### EvidenceValueScore

取得byte数やsample数ではない。次への寄与を表す。

- project go／no-go／commit判断
- defect detectionとquality management
- uncertainty reductionと安心材料
- rework回避とschedule短縮
- 再利用可能な証拠・baseline・回帰データ
- 規格、契約、実験目的上の必要性

## 3. 暫定表示profile

profile ID: `ja-JP-cat-v0`

両scoreは暫定的に0〜300の順序表示へmappingする。300超は`300+`表示とし、数値精度を装わない。

| ExecutionRiskScore | 表示band |
|---:|---|
| 0–99 | low |
| 100–179 | guarded |
| 180–199 | moderate |
| 200–249 | high |
| 250+ | very-high |

| EvidenceValueScore | 表示band |
|---:|---|
| 0–49 | marginal |
| 50–99 | reassurance |
| 100–199 | quality-value |
| 200–249 | decision-value |
| 250+ | project-commit-value |

このbandはメッセージroutingの暫定値で、操作許可へ使わない。実測runと人間間コミュニケーションの
評価後にversionを上げる。旧ゲシュタルト0〜500式から換算しない。

## 4. ガイダンス入力

```json
{
  "profile_id": "ja-JP-cat-v0",
  "scale_kind": "ordinal_metaphor",
  "time_scope": "PROSPECTIVE",
  "risk_evidence_state": "PROJECTED",
  "benefit_evidence_state": "PROJECTED",
  "execution_risk_score": 200,
  "evidence_value_score": 250,
  "evidence_necessity": "QUALITY_OR_DECISION",
  "unknown_count": 1,
  "missing_roles": ["engineer"],
  "message_locale": "ja-JP"
}
```

`evidence_necessity`は`REQUIRED`、`QUALITY_OR_DECISION`、`OPTIONAL_REASSURANCE`、`UNKNOWN`を持つ。
`UNKNOWN`をoptionalへ推測しない。

測定前ガイダンスでは冒頭またはbadgeで「測定前予告」を示す。`PROJECTED`を`OBSERVED`と読み上げない。

## 5. 必須受入例

### Case A: risk 200 / value 250

> 測定前予告です。執行対象リスクは200、取得エビデンス価値は250です。プロジェクト継続・commit判断へ強く寄与する
> 可能性がある一方、危険性があります。必要な人員とcheckを揃え、計画を監査してから判断してください。

推奨action: `ESCALATE_WITH_ENABLEMENT`

### Case B: risk 180 / value 100

> 測定前予告です。執行対象リスクは180、取得エビデンス価値は100です。一定のリスクがありますが、未確認点を潰すことで
> 品質管理へ寄与します。対象範囲を限定し、必要checkを確認してください。

推奨action: `REVIEW_FOR_QUALITY_VALUE`

### Case C: risk 250+ / value 50 / evidence optional

> 測定前予告です。執行対象リスクは250を超え、取得エビデンス価値は50です。主な価値が安心材料に留まり、必須
> エビデンスでない場合、この測定は推奨しません。代替手段、延期、または計画縮小を検討してください。

推奨action: `PREFER_ALTERNATIVE_OR_DEFER`

`evidence_necessity=REQUIRED`なら同じscoreでも「推奨しません」で終わらせず、必要性、代替不能理由、
増員、保護策、残余riskをdecision packetへ上げる。

## 6. 文生成規則

自由生成LLMの一回出力を正本にしない。version付きtemplateへ値と理由コードを埋め、次の順序で作る。

1. riskとevidence valueの数値
2. 得られる価値
3. riskまたはunknown
4. 何を足せば進めるか、または代替・延期
5. 実行ゲートとは別であること

文面は責任追及から始めず、価値、曝露、必要支援、決定待ちの順で提示する。決裁者向けの翻訳結果が
Engineer viewのunknown、定格、実行不能判定を上書きしない。

画面には`message_id`、`template_version`、snapshot ID、理由コードを保持し、`why this guidance`から
Engineer viewへdrill-downできるようにする。

## 7. 音声合成

### status lamp音声例

- blue: 「現場状態は青。観測・記録支援中です。物理状態の変更はありません」
- yellow: 「現場状態は黄。追加確認員を要請してください。対象作業のcheckが不足しています」
- red: 「現場状態は赤。停止権限と復旧対応能力を持つ体制が揃うまで、執行を開始しません」
- gray-black: 「現場状態は不明。判定材料が不足しています。新規執行はblockされています」

音声は個人名を危険係数と結び付けず、operationと必要な組織能力を読む。

- 画面表示文を正本とし、TTS専用の別判断を作らない
- mode、band、unknown、必要人員、推奨actionの変化時だけ自動読上げ候補にする
- 同一message IDをdeduplicateし、rate limitとquiet timeを持つ
- mute、再読、acknowledge、速度、声量、voiceをユーザーが設定できる
- scoreだけでなく価値、risk、次のactionを読む
- `SCPI`、`GND`、機種名等の日本語pronunciation dictionaryを持つ
- TTS失敗を測定失敗や承認拒否へ変換しない
- TTS runtimeは実機IP、ApprovalSession token、SCPI権限を持たない

### Machine-translation guardrail (en-US)

The two scores are presentation values, not instrument permissions. Guidance text explains the
risk-benefit impression and the next human decision. They are not money, probability, ROI, damages,
or company valuation. Speech is an optional rendering of the same message.
