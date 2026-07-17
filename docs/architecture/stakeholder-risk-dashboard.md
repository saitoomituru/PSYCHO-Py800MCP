# Stakeholder Risk Dashboard

状態: `[DESIGNED]`

## 1. 目的

技術を専門としない管理者、人事、出資者、現場責任者へ、現在の作業が単なる観測補助なのか、
自動検査の計画監査中なのか、物理リスクを伴う実行中なのか、増員が必要なのかを一目で伝える。
PSYCHO-PASSの犯罪係数風の比喩は、複雑な技術状態を短時間で共有するために使う。

責任を金銭曝露として見る読み手には、役割名だけでなく「何を壊し得るか」「停止と再試験にいくら・
何日かかり得るか」「増員費用と未確認の曝露はどちらが大きいか」を提示する。

本Dashboardは安全判定器、承認者、規格適合判定器ではない。技術ゲートのread-only projectionである。

## 2. 想定する読み手

- 技術詳細を追わない管理者・人事
- 予算と人員を決める出資者・責任者
- 複数作業を俯瞰するラボ管理者
- 現場へ追加要員を呼ぶか判断する当番者

`[POEM]` 現場を後ろから歩く偉い猫が、回路図を読めなくても「今は見るだけ」「次は監査」「赤なら
人を増やす」を一秒で掴むためのメタGUI。ただし表示を見た猫が実行権限を持つわけではない。

## 3. 表示する正本状態

- work mode: observation / analysis / planning / approved execution / stopping / blocked
- hazard delta: none / neutral / may increase exposure / unknown
- MeasurementPlan ID、hash、版、期限
- 計画責任者、監査者、実行担当者
- Dev Check、Engineer Checkの充足・期限・対象点一致
- unknown、deviation、failed checkの件数と最重要理由
- 現在step、次step、中止状態
- 推奨人員数と不足している役割
- 根拠snapshot IDと最終更新時刻
- operational accountability chain
- cost exposure range、currency、根拠、confidence
- legal liability statusと参照した契約・保険・法域資料の有無

## 4. 表示原則

### 4.1 観測は観測として表示する

ユーザーがすでにプローブしている画面、数値、既存buffer、camera、KiCad等をAIが読むだけなら
`OBSERVING / 観測・記録支援中`と表示する。AIが人間の目視・数値ログを補助しているだけであり、
測定開始や入力曝露変更として数えない。

### 4.2 自動検査は責任線を表示する

AIが測定開始、再arm、入力経路変更、連続検査を計画するときは、係数だけでなく次を大きく表示する。

- 誰が計画を作ったか
- 誰が監査するか
- Dev CheckとEngineer Checkが誰により、いつ、何を対象に行われたか
- 実行責任者と中止担当
- 追加で必要な人数と役割

### 4.3 色だけで伝えない

色、状態語、アイコン、数字を併用する。青／緑を「絶対安全」と表現せず「観測のみ」「保存解析のみ」と
具体的に書く。黄は計画・確認待ち、赤は破壊方向または高リスク実行、灰／黒はunknown・blockedを示す。

### 4.4 係数単独で決めない

係数は並べ替え、通知、人員配置説明のための派生値。実行ゲートは`hazard_delta`、MeasurementPlan、
Dev Check、Engineer Check、ApprovalSessionを直接評価する。Dashboardから承認を生成しない。

### 4.5 三種類の「責任」を混ぜない

#### OperationalAccountability

誰が提案、計画、監査、承認、実行、中止、事故対応を担当するか。これはrunとplanへ記録できる。

#### CostExposure

技術的に想定される損失range。機材・probe・DUT交換、lab停止、再試験、再校正、失われるデータ、
schedule、incident response、第三者影響、追加人員費を含む。各値へ根拠、入力者、時点、confidenceを付ける。
不明値を0円にしない。

#### LegalLiabilityStatus

誰が法的賠償責任を負うかは、契約、保険、雇用関係、法域、事故事実に依存する。AIは
OperationalAccountabilityやCostExposureから法的責任者を推定しない。必要資料がなければ
`UNDETERMINED`と表示し、法務・保険・組織決裁の確認先を示す。

### 4.6 人を呼ぶ経済理由を見せる

`staffing_delta`として、必要役割、現在人数、不足人数、追加確認の所要時間・概算費用を表示する。
その横へ、確認を省略した場合のCostExposure rangeと未確認項目を置く。Dashboardは費用対効果の材料を
提示するが、「安いから危険作業を許可する」という判断を自動化しない。

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
│ [open evidence] [open plan] [who is needed]│
├─ MONEY / ACCOUNTABILITY ───────────────────┤
│ staffing delta: +1 engineer / <range>       │
│ cost exposure: <low> .. <high> / UNKNOWN   │
│ legal liability: UNDETERMINED               │
│ owner: plan / review / execute / stop       │
└────────────────────────────────────────────┘
```

## 6. データ境界

Dashboard入力はschema version付きの状態snapshotとartifact IDだけにする。生波形、規格本文、任意path、
ApprovalSession token、SCPI資格情報を受け取らない。表示操作から実機コマンドを送れない構造にする。

### Machine-translation guardrail (en-US)

The dashboard is a lossy communication view for nontechnical stakeholders. It never grants instrument
authority. A low score does not approve an action, and a high score does not replace the underlying
engineering evidence, plan review, or staffing decision. Cost exposure is not a legal-liability finding.
