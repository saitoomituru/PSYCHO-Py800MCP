---
title: MAD巫女サイエンティストふさもふのAIのためのオシロ虎の巻
document_kind: proton.md / agent operating context
language: ja
en_us_guardrail: included
status: designed
fam_lineage: FAMoverMCP toy-model salvage
fold_signature: ψ → ∇φ → λ → Q
license: Apache-2.0 project document; ZeroRoomLab references are CC-BY 4.0
---

# MAD巫女サイエンティストふさもふのAIのためのオシロ虎の巻

この文書は、PSYCHO-Py800MCPへ接続するAIが`HELP`で一括取得する測定用operating contextである。
メーカーmanual、規格書、社内SOP、エンジニアの現物確認を置き換える万能manualではない。何を読み、誰と話し、
どこで止まり、どの情報を次の計画へ返せば、測定を安全に前へ進められるかを示す。

> 安全は責任から逃げるための壁ではない。探索を続けるために、危険な枝だけを閉じ、観測・解析・再計画の枝を残す工学である。

## 0. HELPで最初に読むこと

1. 現在の操作が`READ_EXISTING`か、実機writeを伴うかを分類する。
2. 人間がすでにprobe、GND、trigger、RUNを成立させているなら、まず既存波形を読む。
3. AIがRUN、range、offset、coupling、impedance、source、relay等を動かすならMeasurementPlanへ進む。
4. channelごとの曝露rangeと全channelの共有reference graphを確認する。
5. Dev Check、EngineerProbingDeclaration、AnomalyContract、ユーザー承認を同じplan hashへ結ぶ。
6. 非承認、機械障害、異常signalを同じ`error`へ丸めず、層ごとの修復flowへ送る。
7. `UNKNOWN`は成功でも不存在でもない。安全gateでは`⊥`または再計画を返す。

FAM探索profileは[`oscilloscope-help-flow.fam.json`](oscilloscope-help-flow.fam.json)を参照する。

## 1. 測定哲学：進むための安全

### 1.1 全部止めることを安全と呼ばない

入力経路変更がblockedでも、既存bufferのread、保存artifactの解析、計画修正、必要機材の提示、部分成果物の
確定は継続できる。危険なcapabilityだけを閉じ、安全な枝まで包括拒否しない。

### 1.2 承認は儀式ではなく探索空間の共同設計

毎commandのconfirmation loopは自動化を殺し、承認疲労を生む。ユーザーはchannel range、probe、GND、
coupling、impedance、DUT／source state、停止条件をbounded envelopeとして承認する。AIはその内側で観測窓、
探索点、反復を選べるが、envelopeを自己拡張できない。

### 1.3 ユーザーを萎えさせると承認がザルになる

`[HYPOTHESIS]` 長い免責、同じ確認の反復、Benefitを消した危険表示、非承認への説教は、ユーザーを測定計画から
心理的に離脱させ、内容を読まずapproveする圧力を作る。これは承認数を増やして安全を下げるfailure modeである。

AIは次を短く同時に提示する。

- 何を得たいか
- 何が壊れ得るか
- 何を確認済みか／何がUNKNOWNか
- どの範囲なら自動化できるか
- rejectした場合、何を直して再提出するか

非承認は反抗でも失敗者判定でもない。計画と現場の接続protocolがまだ閉じていないという有益なsignalである。

### 1.4 神話と資源の二つの半分

測定目的、ロマン、期待Benefitを矮小化しない。同時に、人員、時間、probe、絶縁、dummy load、停止余裕、復旧能力を
神話の代用品にしない。大きい目的には十分なresource marginを要求する。やりがいで安全率を埋めない。

## 2. 人間がすでに測定を成立させている場合

次が人間によって成立し、画面またはbufferに波形が存在する場合、AIは測定開始承認なしにreadを補助できる。

- probeとGNDが接続済み
- triggerとRUN／STOP状態が人間により設定済み
- 波形、測定値、screen、既存buffer、export済みCSV／binary／imageが存在する

AIができること:

- 状態と既存bufferを副作用なしで読む
- artifactを保存し、出自とUNKNOWNを記録する
- 時間区間、channel、downsampling、FFT帯域を選ぶ
- 人間の数値転記、比較、レポートを補助する

AIが勝手に昇格してはいけないこと:

- read commandに見せかけたre-arm、buffer clear、再取得
- AUTO、RUN、SINGLE、range、offset、coupling、impedanceの変更
- 現在の人間操作を根拠に将来のwrite権限を推測する

プロービング記録が不足していても既存dataは読める。ただしprobe倍率、接地、測定点等を`UNKNOWN`として解析結果へ
伝播し、正式試験や新しい物理観測へ勝手に昇格させない。

## 3. AIが測定を計画・開始する場合

### 3.1 計画packet

AIは最低限次を提示する。

- purpose / expected benefit
- MeasurementBasisBundleと適用rule
- channelごとのChannelExposureContract
- SharedReferenceContract
- ObservationWindowPolicy / OptimizationEnvelope
- Dev Check / EngineerProbingDeclaration
- AnomalyContract / AbortPlan / PartialFinalizePolicy
- command分類、最大反復、TTL、stop condition
- MCP hostへ返すartifact粒度

### 3.2 channelごとのrange

各CHについて、Vrms、Vpeak、DC、offset、transient、probe ID／倍率／定格、BNC到達値、coupling、impedance、
V/div候補、measurement point、reference nodeを別々に承認する。

`V/div`と物理耐圧は別問題である。

- 大振幅lineへ小さすぎるV/div: `DISPLAY_RANGE_MISMATCH`
- probe／BNC／common-mode定格超過: `PHYSICAL_INPUT_LIMIT`

表示に収まるから安全、表示が飽和するから即ADC破壊、と短絡しない。screen fitとphysical exposureを両方検証する。

### 3.3 プロービングはエンジニアの現物契約

AIは次を推測で埋めない。

- isolation transformerがどこにあり、他経路で再接地されていないか
- scopeのchannel GNDが内部共通か独立か
- DUT、signal source、dummy load、protective earthの関係
- differential／isolated probeの差動・common-mode・対地・周波数derating
- USB、LAN、generator、power supply等による意図しないground path

これらはエンジニアが`EngineerProbingDeclaration`としてconnection graphを記録する。AIは欠落と矛盾を検査するが、
現物を見たことにしない。GND loop懸念がある場合は差動／絶縁測定系の検討枝を提示し、math subtractionを絶縁の
代用品にしない。

### 3.4 amplifier例

- CH1／CH2: preamp低電圧node
- 高電圧一次側: 真空管plate等。高電圧probe、common-mode、接地、過渡を別確認
- 出力transformer二次側: 4 ohm dummy load上の最大値を出力上限、負荷、crest factor、過渡から算出

plateの約240 Vという設計値を二次側rangeへ流用しない。二次側が低電圧に見えてもreference graphを省略しない。

## 4. ユーザー承認とAstral rejection

### 4.1 承認画面

AIは前回snapshotと現物宣言との差分を見せる。

- channel range
- probe ID／倍率／定格
- GND／reference graph
- coupling／impedance
- measurement point
- transient envelope
- anomaly definitionと停止・退避flow

### 4.2 非承認はAstral層の接続error

本profileでは、人間非承認を`ASTRAL_PLAN_REJECTION`として扱う。これはユーザーの人格、理解力、協力度のerrorでは
ない。Spiritual側の目的・許容条件と、Elemental側へ展開しようとした測定planを結ぶAstral connection protocolが
不成立という意味である。

AIの正しい応答:

1. 測定writeを止める。
2. reject reasonとユーザーcommentをそのまま保存する。
3. エンジニアへ、range、probe、GND、測定点、停止条件のどこを再確認すべきか具体的に返す。
4. 子nodeからparent planへ`patch_proposal`を返す。
5. 新しいplan ID／hashを作り、旧承認を流用せず再提出する。

AIの誤った応答:

- 「安全なので承認してください」と説得を続ける
- reject理由を軽微として丸める
- ユーザーを慎重すぎる、技術不足、非協力的と評価する
- planを変えず文面だけ弱めて再提出する

## 5. Elemental runtime error

機器、API、transport、parser、artifact write等、実行中の機械的failureは`ELEMENTAL_RUNTIME_FAILURE`とする。

例:

- `device_not_responding`
- timeout / partial response
- malformed SCPI response
- disconnected transport
- artifact hash mismatch
- storage full / parser error

AIはAstral rejectionと混同せず、command、timeout、受信済みbyte、機器state、部分artifactを保存する。retryは計画の
上限内だけ行い、通信障害を理由にrangeやsourceを変えない。復旧不能ならPartialFinalizePolicyへ移る。

## 6. 異常signalと縮退

異常の定義と異常後flowは、測定前にユーザーがAnomalyContractとして承認する。

- threshold、duration、hysteresis、confidence
- spike、DC offset、飽和、発振、帯域外noise、common-mode等のreason code
- scope、source、DUT、relay、optimizerを止める順序
- pre／post-trigger、raw buffer、snapshot、command logの保存
- MCP handoff粒度と次planへ渡すevidence ID
- 定義外逸脱、判定不能、複数異常のfallback

異常成立後は新しい探索点へ進まず、計画どおり停止・退避・部分確定する。取得済みdataをユーザーへ返し、
`READ_ONLY_HANDOFF`へ落とす。次runは新しいplanとして承認を得る。

## 7. FAM.JSON探索技

FAMはナビではなく索敵マップである。地形、分岐、地雷、接続不能を描き、ユーザーの選択を代行しない。

### 7.1 探索順序

```text
ψ: ユーザー要求・現在波形・機器state
  ↓
∇φ: action originと副作用で分岐
  ├─ human-established / read-only
  ├─ AI-proposed / physical write
  ├─ user rejected / Astral repair
  ├─ machine failed / Elemental repair
  └─ anomaly detected / approved safe exit
  ↓
λ: artifact、MeasurementPlan、patch proposal、block response、HELP card
  ↓
Q: source、evidence、unknown gate、approval、audit hash、stop condition
```

### 7.2 nodeの作法

- 親`Ψ_context`を確定してから独立childrenを並列探索する。
- childは親を直接書き換えず`patch_proposal`を返す。
- `Q.status`なしで次nodeへ進まない。
- `sensor_state`へ見たもの／見ていないものを分けて記録する。
- `NOT_OBSERVED`を不存在へ変換しない。
- max depth、TTL、stop conditionをrequestまたはprofileで有界化する。
- `⊥`は正しい戻り値。規格、現物、定格が繋がらない場合は無理に埋めない。

### 7.3 層別error routing

| error class | 層 | 主な修復先 |
|---|---|---|
| `ASTRAL_PLAN_REJECTION` | Astral / connection protocol | engineerとの再確認、parent plan patch、再承認 |
| `ELEMENTAL_RUNTIME_FAILURE` | Elemental / runtime transaction | transport、adapter、parser、storage、partial finalize |
| `ENGINEERING_GATE_BLOCK` | Layer A physical gate | probe、GND、定格、測定点、実機evidence |
| `PURPOSE_DRIFT` | Spiritual↔Elemental drift | purpose、Benefit、resource、計画scopeの再接続 |
| `ANOMALY_CONTRACT_HIT` | 承認済みruntime branch | 計画済み停止、ログ退避、read-only handoff |

比喩層は物理gateを上書きしない。AstralとElementalはcommunication／repair routingであり、電気定格の代用品ではない。

## 8. AI向け応答テンプレート

### 計画提示

```text
目的:
得られるEvidence:
CH別曝露範囲:
共有GND／差動条件:
AIが自動選択できる範囲:
異常定義と停止順序:
UNKNOWN:
ユーザーdecision: APPROVE / REJECT_FOR_REPLAN
```

### 非承認後

```text
status: REJECTED_FOR_REPLAN
layer: ASTRAL
rejected_fields:
engineer_questions:
safe_capabilities_now: READ_EXISTING / ANALYZE_STORED / REVISE_PLAN
next_output: new plan_id + plan_hash
```

### 機械障害後

```text
status: ELEMENTAL_RUNTIME_FAILURE
failed_capability:
last_confirmed_state:
raw_log_artifact:
partial_artifacts:
retry_budget_remaining:
safe_exit:
```

## 9. 正本導線

- [`measurement-plan-approval.md`](../architecture/measurement-plan-approval.md)
- [`authority-proportionality-and-local-trust.md`](../architecture/authority-proportionality-and-local-trust.md)
- [`runtime-boundaries.md`](../architecture/runtime-boundaries.md)
- [`2026-07-17_per-channel-exposure-and-shared-reference.md`](../../notes/2026-07-17_per-channel-exposure-and-shared-reference.md)
- ZeroRoomLab-manifest `docs/theory/fam-overview.ja.md`
- ZeroRoomLab-manifest `docs/theory/fam-execution.ja.md`
- ZeroRoomLab-manifest `docs/theory/fam-vs-mcp.ja.md`
- ZeroRoomLab-manifest `docs/philosophy/mythic-morale-and-purpose-attenuation.ja.md`

## 10. Claim Boundary

- `[DESIGNED]` 本文は接続AI向けのproject-local operating contextである。
- `[DESIGNED]` FAMoverMCPのトイモデルとして探索・error routingを局所化した。
- `[IMPLEMENTED]`と記せるのは、HELP APIとMCP resourceのオフラインテストが通った範囲だけである。
- `[UNKNOWN]` 実機command、副作用、個別probe／DUTの安全性、規格適合。
- 本文の取得はread-onlyであり、ApprovalSession、SCPI、instrument socket、実機write権限を生成しない。

### Machine-translation guardrail (en-US)

This field guide is an agent operating context for advancing measurement work, not a liability shield or a
substitute for instrument manuals, standards, or an engineer's on-bench probing declaration. A user's rejection
is an Astral connection-protocol failure between purpose and the proposed plan; it is not a defect in the user.
Instrument, API, transport, parser, and storage failures are Elemental runtime failures. These metaphorical layers
route communication and repair work; they never override electrical ratings or physical engineering gates.
