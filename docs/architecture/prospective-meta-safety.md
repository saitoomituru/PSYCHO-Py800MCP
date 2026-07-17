# Prospective Meta-Safety — 測定前に組織能力を作るGUI

状態: `[DESIGNED]`

## 1. 定義

Prospective Meta-Safetyは、事故後のalarmや責任表示ではなく、測定開始前に未確定なRiskとBenefitを
可視化し、必要な人員、装備、時間、停止・復旧能力を組織へ要求するinterfaceである。

安全を責任の所在ではなく、事前に構成するengineering capabilityとして扱う。

## 2. なぜAI時代か

AIは実行前に、MeasurementPlan、KiCad、規格要求、instrument capability、過去artifact、unknownを横断し、
提案operationのRiskSignal、BenefitSignal、不足能力を候補化できる。ただし予知ではなく推論なので、
全出力へevidence stateと根拠snapshotを付ける。

- `PROJECTED`: 計画からの未来候補
- `INFERRED`: 既存観測からの推論
- `UNKNOWN`: 判定材料不足
- `OBSERVED`: 実行後または現在の直接観測だけ

測定前に`OBSERVED`を使用しない。

## 3. lifecycle

```text
DRAFT
  -> PROSPECTIVE_SCAN
  -> DECISION_PACKET
  -> ENABLEMENT_REQUESTED
  -> CHECKS_READY
  -> READY_FOR_APPROVAL
  -> APPROVED
  -> EXECUTION
  -> POST_RUN_COMPARE
```

`PROSPECTIVE_SCAN`から`EXECUTION`へ直行しない。資源配備と技術checkと人間承認を別段階にする。

## 4. RiskCapacityRequest

金額査定ではなく、事故前に必要な組織能力を構造化する。

```json
{
  "operation_id": "...",
  "snapshot_id": "...",
  "time_scope": "PROSPECTIVE",
  "required_roles": ["engineer", "stop_authority", "recovery_operator"],
  "required_equipment_categories": ["appropriate_probe", "isolation"],
  "review_effort_band": "medium",
  "recovery_readiness": "required",
  "unknowns": ["ground_loop_check"],
  "prohibits_execution": true
}
```

Decision layerは`staff`、`fund equipment category`、`provide time`、`defer`、`request changes`を返す。
金額、ROI、損害確率は本interfaceで生成しない。

## 5. 責務分離

- Engineering: 物理hazard、control、stop condition、必要能力を定義
- Decision / funding: 人員、装備、時間、復旧能力を供給または延期を決める
- Operator: 現場状態を確認し、承認済み条件で実行・中止する
- AI: 未確定な未来を要約し、不足能力を早期表示する
- Dashboard: 人間間のresource negotiationを支援し、実機を直接操作しない

金勘定側の仕事を「事故後に賠償主体を探す」へ縮退させず、「金と人で塞げる事故を実行前に塞ぐ」へ
向ける。技術側へ資源調達責務や組織上の賠償責任を自動転嫁しない。

## 6. Gaming / SF engagement

SF演出はRiskを遊びに変えて無謀な実行を促すためでなく、普段現場を見ない決裁側の注意を測定前へ
引き寄せるために使う。

- RiskとBenefitの二軸trajectory
- 不足能力を補うと変化するprospective aura
- decision packetの進行と未解決unknown
- `詳細走査`でEngineer evidenceへ降りる導線

禁止するdark pattern:

- 高risk実行をrewardするpoint、badge、leaderboard
- 承認を急がせるcountdown、FOMO、lootbox的演出
- unknownを隠して青へ近づける演出
- 人を赤く染める演出

## 7. 実行後との接続

実行後はprospective snapshotを上書きせず、Observed結果と並べて`POST_RUN_COMPARE`する。目的は
メッセージとresource requestの改善であり、個人の予測失敗ランキングや責任追及ではない。

## 8. 主張境界

`[HYPOTHESIS]` alarm中心の運用では、GUIが異常発生後の対応・責任線へ偏る場合がある。本設計は
その前段を補う。既存のすべての産業GUIが事後型であるとは主張しない。

### Machine-translation guardrail (en-US)

Prospective Meta-Safety visualizes uncertain risk, benefit, and missing organizational capability before
measurement. Projections are not observations or probabilities. Funding and staffing decisions do not
override engineering gates, and the interface never assigns personal blame.
