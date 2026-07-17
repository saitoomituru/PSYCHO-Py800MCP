# Purpose Function Ledger — 目的と資源安全率の減衰監査

状態: `[DESIGNED]`

上位哲学正本: ZeroRoomLab-manifest
[神話的士気管理と目的関数矮小化連鎖](https://github.com/saitoomituru/ZeroRoomLab-manifest/blob/main/docs/philosophy/mythic-morale-and-purpose-attenuation.ja.md)

本書はLayer Aの設計契約であり、神話、夢、ロマン、哲学の内容を採点しない。

## 1. 目的

資金、計画、管理、実行の各stageを通る間に、実験の原初目的、期待Benefit、安全control、必要資源が
どのように保持・変更・削減されたかを追跡する。最後に見えた確認省略を個人の怠慢だけへ縮約せず、
上流で起きた目的関数とresource marginの減衰を調査可能にする。

本台帳は士気score、人事評価、忠誠心検査ではない。対象は`operation_id + snapshot_id`とstage間の
変更であり、人物を赤く染めない。

## 2. 二つの独立signal

### PurposeIntegritySignal

原初の目的、得たい知識、守る品質、project option、撤退条件が、現在の計画から辿れるかを表す。

- `PRESERVED`: 原初目的と現在stepの接続が記録されている
- `ATTENUATED`: 一部が代理KPIまたは局所都合へ縮約された
- `SEVERED`: 現在stepから上位目的を辿れない
- `UNKNOWN`: 根拠不足

### ResourceIntegritySignal

目的を執行する人員、時間、装備、予算category、停止余裕、復旧能力、安全率が計画に残っているかを表す。

- `MARGIN_RECORDED`: 必要量と余裕の根拠が記録されている
- `MARGIN_REDUCED`: 余裕削減と下流影響が記録されている
- `INSUFFICIENT`: 必要能力を満たさない
- `UNKNOWN`: 根拠不足

どちらも順序signalであり、事故確率、士気率、金額、個人能力へ変換しない。

## 3. 二軸状態

| Purpose | Resource | 表示と処置候補 |
|---|---|---|
| preserved | margin recorded | 目的と物質条件が接続済み。別途、通常の技術gateを評価する |
| preserved | reduced / insufficient | `EXPLOITATION_RISK`。使命やロマンで不足資源を埋めず、staff/fund/deferへ戻す |
| attenuated / severed | margin recorded | `PURPOSE_DRIFT`。原初目的と現在stepを再接続し、不要なら中止・再設計する |
| attenuated / severed | insufficient | `ORGANIZATIONAL_COLLAPSE_CANDIDATE`。現場の気合で進めず上流へ差し戻す |
| any | unknown | unknown gate。青・低riskへ丸めない |

この表はMeasurementPlan承認や実機権限を生成しない。

## 4. append-only schema

```json
{
  "ledger_id": "pfl-...",
  "operation_id": "op-...",
  "snapshot_id": "snap-...",
  "original_purpose": {
    "narrative_ref": "user-supplied-or-project-canonical-ref",
    "expected_benefits": ["..."],
    "protected_values": ["..."],
    "exit_conditions": ["..."]
  },
  "non_negotiable_controls": ["..."],
  "resource_assumptions": {
    "roles": ["..."],
    "equipment_categories": ["..."],
    "time_margin_band": "...",
    "recovery_readiness": "...",
    "unknowns": ["..."]
  },
  "events": [
    {
      "stage": "funding|planning|management|execution",
      "change_kind": "preserve|clarify|reduce|remove|defer",
      "target": "purpose|benefit|control|resource|margin|exit_condition",
      "reason": "...",
      "downstream_effect": "...",
      "evidence_refs": ["artifact-id"],
      "acknowledgement_state": "pending|accepted|rejected|unknown"
    }
  ],
  "purpose_integrity": "PRESERVED|ATTENUATED|SEVERED|UNKNOWN",
  "resource_integrity": "MARGIN_RECORDED|MARGIN_REDUCED|INSUFFICIENT|UNKNOWN"
}
```

過去eventを上書き・削除せず、訂正も新eventで行う。自由記述だけでなく、対象、理由、下流影響、根拠、
受領状態を残す。

## 5. Decision Packetへの統合

Executive viewには次を短く表示する。

- この測定が接続する原初目的と期待Benefit
- 目的関数が縮小されたstageと、失われる選択肢
- 必要なresource marginと現在の不足
- `EXPLOITATION_RISK`または`PURPOSE_DRIFT`
- `fund / staff / restore margin / reconnect purpose / defer / stop`の候補

Engineer viewには変更event、技術control、根拠artifact、unknownを表示する。要約と詳細は同じ
`ledger_id + snapshot_id`を参照する。

## 6. 禁止事項

- mission、情熱、ロマンを賃金、人員、時間、装備、安全controlの代替にする
- 個人の士気、忠誠心、熱意、協調性をscore化する
- 不満、恐れ、疲労、異議を低士気として自動抑制する
- 資源不足を「目的への共感」で解消済みにする
- 目的の美しさからApprovalSession、SCPI権限、測定開始を生成する
- PurposeIntegritySignalから事故原因や人物責任を自動断定する

## 7. 受入条件

- 原初目的から現在stepまでの変更履歴を辿れる
- 目的とresource marginを独立表示できる
- purpose preserved / resource insufficientを明示的に`EXPLOITATION_RISK`と表示できる
- unknownを低riskまたは充足へ変換しない
- event訂正後も旧記録が残る
- Dashboardを無効化しても技術gateと実機権限が変化しない
- person IDなしで全状態を表現できる

### Machine-translation guardrail (en-US)

The Purpose Function Ledger tracks how project purpose and material safety margin change across funding,
planning, management, and execution. Purpose and resources are independent requirements. A strong mission
with insufficient resources is an exploitation warning, not evidence that work may proceed. The ledger never
scores employee loyalty, morale, or character and never grants instrument authority.
