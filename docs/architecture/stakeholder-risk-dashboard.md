# Stakeholder Risk-Benefit Dashboard

状態: `[DESIGNED]`

## 1. 目的

技術を専門としない管理者、人事、出資者、現場責任者へ、現在の作業が単なる観測補助なのか、
自動検査の計画監査中なのか、物理リスクを伴う実行中なのか、増員が必要なのかを一目で伝える。
PSYCHO-PASSの犯罪係数風の比喩は、複雑な技術状態を短時間で共有するために使う。

責任追及だけを強く見せると、複雑な仕事を避ける、または賠償能力のある権威者へ判断を丸投げする
権力倒れが起きる。主画面ではRiskExposureとBenefitProjectionを対にして、「何が得られるか」
「何を失い得るか」「何を足せば進めるか」「誰の決定が必要か」を示す。

本Dashboardは安全判定器、承認者、規格適合判定器ではない。技術ゲートのread-only projectionである。

Devと現場エンジニアは、定格、波形、GND、接続条件から危険の兆候を読む専門側であり、本Dashboardの
主たる教育対象ではない。解消したいのは、専門側の「この条件は香ばしい」が、予算、停止損失、品質、
schedule、project optionへ翻訳されず、金銭と決裁だけを見る層に届かない情報断絶である。

## 2. 主対象と根拠提供者

### 主対象

- 技術詳細を追わない管理者・人事
- 予算、人員、継続、延期を決める出資者・決裁者
- 複数作業を俯瞰するラボ管理者
- 現場へ追加要員を呼ぶか判断する当番者

### 根拠提供者

- Dev: 設計想定範囲、期待値、project benefit、技術計画
- Engineer: 現物状態、定格、probe、GND、leakage、実行可能性

Engineer viewは専門家向けの根拠正本であり、初心者向け説明へ単純化しない。Executive viewは同じ
snapshotを資本、schedule、品質、option value、必要支援へ翻訳する。

`[POEM]` 現場を後ろから歩く偉い猫と、プローブを握る現場猫のあいだで、「怖いからやめろ」と
「技術が分からないなら黙れ」を往復させない猫間プロトコル。赤でも旨い魚があるなら、人と予算と
確認を足して取りに行く。ただし表示を見た猫の肉球で安全ゲートは開かない。

`[POEM]` 裏の金勘定しか見えない責任者へ、現場の「おっと香ばしい」を、壊れる金額と守れる品質と
取りに行ける価値へ翻訳する。専門家を再教育するのでなく、決裁側の盲点を減らす。

## 3. 表示する正本状態

- work mode: observation / analysis / planning / approved execution / stopping / blocked
- hazard delta: none / neutral / may increase exposure / unknown
- MeasurementPlan ID、hash、版、期限
- DecisionRoleMap: propose / review / decide / fund / staff / execute / stop
- Dev Check、Engineer Checkの充足・期限・対象点一致
- unknown、deviation、failed checkの件数と最重要理由
- 現在step、次step、中止状態
- 推奨人員数と不足している役割
- 根拠snapshot IDと最終更新時刻
- risk exposure range、currency、根拠、confidence
- benefit projection、単位、range、根拠、confidence
- staffing・reviewを追加した場合のresidual risk
- legal liability statusと参照した契約・保険・法域資料の有無

## 4. 表示原則

### 4.1 観測は観測として表示する

ユーザーがすでにプローブしている画面、数値、既存buffer、camera、KiCad等をAIが読むだけなら
`OBSERVING / 観測・記録支援中`と表示する。AIが人間の目視・数値ログを補助しているだけであり、
測定開始や入力曝露変更として数えない。

### 4.2 自動検査はdecision packetを表示する

AIが測定開始、再arm、入力経路変更、連続検査を計画するときは、責任追及文ではなく、非専門者が
短時間で判断できるdecision packetを表示する。

- benefit: 何を得るか、得られない場合の影響
- risk: 何を失い得るか、unknownは何か
- enablement: 追加すべき人員、予算、check、時間
- decision: 誰がreview、fund、staff、go／no-go／deferを決めるか
- evidence: エンジニア向けplan、Dev Check、Engineer Checkへのdrill-down

### 4.3 色だけで伝えない

色、状態語、アイコン、数字を併用する。青／緑を「絶対安全」と表現せず「観測のみ」「保存解析のみ」と
具体的に書く。黄は計画・確認待ち、赤は破壊方向または高リスク実行、灰／黒はunknown・blockedを示す。

### 4.4 係数単独で決めない

係数は並べ替え、通知、人員配置説明のための派生値。実行ゲートは`hazard_delta`、MeasurementPlan、
Dev Check、Engineer Check、ApprovalSessionを直接評価する。Dashboardから承認を生成しない。

### 4.5 主画面を責任追及UIにしない

#### DecisionRoleMap

誰が提案、review、decision、fund、staff、execute、stopを担当するか。目的は責任を押し付けることではなく、
次の判断が止まっている場所と、誰へ何を頼めば流れるかを明確にすること。

#### RiskExposure

技術的に想定される損失range。機材・probe・DUT交換、lab停止、再試験、再校正、失われるデータ、
schedule、incident response、第三者影響、追加人員費を含む。各値へ根拠、入力者、時点、confidenceを付ける。
不明値を0円にしない。

#### LegalLiabilityStatus

誰が法的賠償責任を負うかは、契約、保険、雇用関係、法域、事故事実に依存する。AIは
DecisionRoleMapやRiskExposureから法的責任者を推定しない。必要資料がなければ
`UNDETERMINED`と表示し、法務・保険・組織決裁の確認先を示す。

LegalLiabilityStatusは通常のgo／no-go主画面へ常時大書きせず、法務確認が必要な場合の詳細panelへ置く。
これにより、すべての技術相談が最初から賠償責任の押し付け合いになることを避ける。

### 4.6 人を呼ぶ経済理由を見せる

`staffing_delta`として、必要役割、現在人数、不足人数、追加確認の所要時間・概算費用を表示する。
その横へ、確認を省略した場合のRiskExposure range、BenefitProjection、未確認項目を置く。Dashboardは
費用対効果の材料を提示するが、「安いから危険作業を許可する」という判断を自動化しない。

### 4.7 Risk × Benefit

| Risk | Benefit | Dashboardの提案 |
|---|---|---|
| low | low | 優先度、試験目的、より軽い代替案を見直す |
| low | high | 通常フローで進める候補 |
| high | low | 再設計、延期、代替測定の候補 |
| high | high | 増員、予算、check、決定権限を揃えるdecision packetへ昇格 |

これは自動決定表ではない。`UNKNOWN`はlow/highへ推測変換せず、必要な確認として別表示する。

### 4.8 二層UI

- **Executive / VC / HR view:** benefit、risk、必要人員・予算、decision待ち、期限を短く表示
- **Engineer view:** MeasurementPlan、コマンド、副作用、定格、根拠artifact、check、deviationの正本を表示

両画面は同じsnapshot IDを参照し、要約と技術詳細の食い違いを防ぐ。管理側は`fund`、`staff`、
`request changes`、`defer`、`decline with reason`を返せるが、実機操作を直接開始できない。
Executive viewの数値や予算判断は、Engineer viewの定格超過、unknown、技術ゲートを上書きできない。

### 4.9 猫間decision handshake

1. Engineer viewから目的、BenefitProjection、RiskExposure、unknown、必要支援をdecision packet化
2. Executive viewは`fund`、`staff`、`request changes`、`defer`、`decline with reason`を返す
3. Engineer viewは返答を技術条件へ反映し、実現可能性、残余risk、未充足checkを更新
4. 実行可能になった計画だけを、別のMeasurementPlan／ApprovalSession承認フローへ渡す

管理側の返答は予算・人員・優先順位のdecision recordであり、測定開始承認そのものではない。
各往復は同じdecision packet IDとsnapshot IDで追跡し、「危ない」「金がない」だけの自由記述往復を減らす。

### 4.10 一文ガイダンスと音声

Executive viewは`ExecutionRiskScore`と`EvidenceValueScore`を数字だけで終わらせず、現在の意味と次の行動を
一文へ戻す。画面上の文を正本とし、音声は同じmessage IDから作る任意出力にする。詳細仕様と受入例は
[`risk-benefit-guidance.ja.md`](risk-benefit-guidance.ja.md)を参照。

音声はscore band、mode、unknown、必要人員が変わった時だけ読み、同一messageを連呼しない。
mute、再読、acknowledge、速度・声量設定を持たせる。TTSエンジンはプレゼンテーションvenvに閉じ込め、
音声入力や読み上げボタンから実機権限を得ない。

## 5. 最小画面

```text
┌─ CURRENT WORK ─────────────────────────────┐
│ OBSERVING / 観測・記録支援中               │
│ AI action: screen + existing buffer read   │
│ Physical state change: NONE                │
├─ NEXT PLANNED ACTION ──────────────────────┤
│ START_MEASUREMENT / 計画監査待ち           │
│ Dev Check: READY  Engineer Check: MISSING  │
│ Staffing: 2 roles required / 1 missing     │
├─ GESTALT PRESENTATION ─────────────────────┤
│ coefficient: <derived>  UNKNOWN: 1         │
│ reason: ground-loop check not recorded     │
│ [benefit] [risk] [what enables progress]   │
│ guidance: <short Japanese recommendation>   │
│ [speak] [mute] [why this guidance]          │
├─ DECISION PACKET ──────────────────────────┤
│ benefit: defect coverage + reusable evidence│
│ risk: <low> .. <high> / UNKNOWN: 1          │
│ staffing delta: +1 engineer / <range>       │
│ decision: fund + staff + review             │
│ [engineer detail] [request changes] [defer] │
└────────────────────────────────────────────┘
```

## 6. データ境界

Dashboard入力はschema version付きの状態snapshotとartifact IDだけにする。生波形、規格本文、任意path、
ApprovalSession token、SCPI資格情報を受け取らない。表示操作から実機コマンドを送れない構造にする。

### Machine-translation guardrail (en-US)

The dashboard is a lossy communication view for nontechnical stakeholders. It never grants instrument
authority. A low score does not approve an action, and a high score does not replace the underlying
engineering evidence, plan review, or staffing decision. Cost exposure is not a legal-liability finding.
Risk and benefit are presented together; complexity alone is not a reason to reject high-value work.
