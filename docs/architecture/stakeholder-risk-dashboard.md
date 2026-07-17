# Stakeholder Risk-Benefit Dashboard

状態: `[DESIGNED]`

## 1. 目的

技術を専門としない管理者、人事、出資者、現場責任者へ、現在の作業が単なる観測補助なのか、
自動検査の計画監査中なのか、物理リスクを伴う実行中なのか、増員が必要なのかを一目で伝える。
PSYCHO-PASSの犯罪係数風の比喩は、複雑な技術状態を短時間で共有するために使う。

責任追及だけを強く見せると、複雑な仕事を避ける、または賠償能力のある権威者へ判断を丸投げする
権力倒れが起きる。主画面ではRiskSignalとBenefitSignalを対にして、「何が得られるか」
「何を失い得るか」「何を足せば進めるか」「誰の決定が必要か」を示す。

二つのsignalは犯罪係数風の順序メタ表記である。円、損害確率、事故率、ROI、賠償額、時価総額を
算出する定量財務モデルではない。目的は「香ばしい」「割に合いそう」「安心材料止まり」を、人間間で
素早く共有することにある。

本Dashboardは安全判定器、承認者、規格適合判定器ではない。技術ゲートのread-only projectionである。

主画面は測定後の犯人探しではなく、測定前のresource allocationを扱う。RiskもBenefitも未発生なので、
`time_scope=PROSPECTIVE`とevidence stateを明示し、未来予測を観測事実へ昇格させない。

UIは、枯れた産業用status lampをsemantic coreとし、PSYCHO-PASS的な係数、走査、オーラ、音声を
engagement themeとして分離する。themeを外しても青／黄／赤／灰黒、状態語、人員要求、block条件が
同じ意味で動作しなければならない。

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

`[POEM]` 裏の金勘定しか見えない責任者へ、現場の「おっと香ばしい」を、壊れ方の重さと守れる品質と
取りに行ける価値へ翻訳する。専門家を再教育するのでなく、決裁側の盲点を減らす。

## 3. 表示する正本状態

- time scope: prospective / live / post-run
- evidence state: projected / inferred / unknown / observed
- work mode: observation / analysis / planning / approved execution / stopping / blocked
- hazard delta: none / neutral / may increase exposure / unknown
- MeasurementPlan ID、hash、版、期限
- DecisionRoleMap: propose / review / decide / fund / staff / execute / stop
- Dev Check、Engineer Checkの充足・期限・対象点一致
- unknown、deviation、failed checkの件数と最重要理由
- 現在step、次step、中止状態
- 推奨人員数と不足している役割
- 根拠snapshot IDと最終更新時刻
- risk signal、reason codes、confidence
- benefit signal、reason codes、confidence
- staffing・reviewを追加した場合のresidual risk band
- user-supplied external decision document ID（存在する場合のみ）
- RiskCapacityRequest: roles / equipment / effort / stop / recovery

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

測定前packetではBenefitとRiskの双方へ`PROJECTED`を表示する。確度不足を演出で隠さず、何を確認すれば
yellowからblueへ、redから実行可能な体制へ移れるかを示す。

### 4.3 色だけで伝えない

色、状態語、アイコン、数字を併用する。青を「絶対安全」と表現せず「観測のみ」「保存解析のみ」と
具体的に書く。黄は計画・確認待ち、赤は破壊方向または高リスク実行、灰／黒はunknown・blockedを示す。

色mappingはproject-localであり、特定規格への適合を主張しない。青は観測、黄は追加確認員要請、赤は
停止権限・復旧・incident handling能力を持つ体制の要請、灰黒は不明・執行不可。色覚、モノクロ印刷、
音声なしでも区別できる状態語、形状、アイコンを必須にする。

### 4.3.1 人ではなく作業を染める

lamp、係数、オーラは`operation_id + snapshot_id`へ付与する。person ID、顔、社員番号、個人評価、
ランキングへ付与しない。黄色・赤の主体は「この作業に必要な組織能力」であり、担当エンジニアの
能力不足や賠償責任を示さない。

- yellow: 組織へ追加reviewer／確認員をrequest
- red: 組織へstop authority、復旧、incident handling能力をrequest
- 禁止: 自動的に特定個人をassign、責任者認定、公開晒し上げする

### 4.4 係数単独で決めない

係数は並べ替え、通知、人員配置説明のための派生値。実行ゲートは`hazard_delta`、MeasurementPlan、
Dev Check、Engineer Check、ApprovalSessionを直接評価する。Dashboardから承認を生成しない。

### 4.5 主画面を責任追及UIにしない

#### DecisionRoleMap

誰が提案、review、decision、fund、staff、execute、stopを担当するか。目的は責任を押し付けることではなく、
次の判断が止まっている場所と、誰へ何を頼めば流れるかを明確にすること。

#### RiskSignal

機材・probe・DUT、lab停止、再試験、再校正、失われるデータ、schedule、incident response、第三者影響を、
順序bandと理由コードで表す。金額、確率、損害額を推計しない。未知をlowへ丸めない。

#### BenefitSignal

欠陥検出、品質管理、学習、再利用可能な証拠、手戻り回避、schedule、project optionへの寄与を、
順序bandと理由コードで表す。ROI、売上、時価総額への寄与を推計しない。

法的賠償責任と正式な財務評価は本Dashboardの判定scope外とする。ユーザーが契約、保険、予算等の
正式資料を別途指定した場合も、Dashboardは内容を係数化せず外部decision document IDとしてlinkする。

### 4.6 人を呼ぶ経済理由を見せる

`staffing_delta`として、必要役割、現在人数、不足人数、追加確認の所要時間とeffort bandを表示する。
その横へ、確認を省略した場合のRiskSignal、BenefitSignal、未確認項目を置く。追加人員の円換算や
費用対効果は計算せず、「人員追加は軽い／重い／unknown」程度のメタ表記に留める。

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

1. Engineer viewから目的、BenefitSignal、RiskSignal、unknown、必要支援をdecision packet化
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

### 4.11 SF theme

SF themeは現場への関心を引くpresentation skinで、semantic coreを書き換えない。

- operation scan lineとsnapshot更新演出
- ExecutionRiskScore / EvidenceValueScoreの大きな二軸表示
- blue / yellow / red / gray-blackのoperation aura
- reason codeと必要roleが展開されるdecision card
- 無機質なTTSと短いtransition sound

刺激の強い点滅、常時警報、音声連呼でalarm fatigueを作らない。theme、animation、soundは個別にoff可能。
テーマのボタンから測定開始、承認、SCPI送信を直接行わない。

### 4.12 Prospective Meta-Safety

安全を「事故後に誰が責任を負うか」ではなく、「事故前にどの組織能力を用意するか」として表示する。

- Engineering: hazard、control、stop condition、必要能力を定義
- Decision / funding: 人員、装備、時間、recovery capacityを配備またはdefer
- Operator: 承認済みの物理条件と計画内で実行
- AI: 未確定な未来のRisk／Benefitと不足能力を先に可視化

`[HYPOTHESIS]` alarm中心の運用では、表示が異常発生後の対応や責任線確認へ偏る場合がある。本GUIは
その隙間を埋める事前interfaceを狙うが、既存の全産業GUIが事後型だとは主張しない。

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
│ risk meta: 200  value meta: 250             │
│ staffing delta: +1 engineer / effort: medium│
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
engineering evidence, plan review, or staffing decision. Scores are ordinal metaphors, not financial findings.
Risk and benefit are presented together; complexity alone is not a reason to reject high-value work.
