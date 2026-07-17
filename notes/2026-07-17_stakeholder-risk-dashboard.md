# 2026-07-17 ゲシュタルト係数メタGUIの責務

状態: `[DESIGNED]` `[Layer A]`

## 検証範囲

- 対象: 技術非専門の管理、人事、出資、現場責任者向けのリスク状態表示
- 対象: 観測補助と自動検査計画の表示分離
- 除外: GUI実装、数値重み確定、実機通信、安全性・規格適合の実証

## 設計判断

- `[DESIGNED]` ゲシュタルト係数は技術ゲートではなく、状態snapshotのread-only projectionとする。
- `[DESIGNED]` プローブ済み画面や値をAIが読む行為は`OBSERVING`で、追加作業リスクを付与しない。
- `[DESIGNED]` 自動検査では計画責任者、監査者、二者確認、必要人員、unknownを係数と併記する。
- `[DESIGNED]` 色だけに依存せず、状態語、アイコン、数字、理由を併記する。
- `[DESIGNED]` DashboardからApprovalSessionや実機操作を生成しない。
- `[SUPERSEDED]` 操作責任線、金銭曝露、法的賠償責任の状態を分離する旧案は、
  `ordinal_metaphor`方針へ置き換えた。
- `[SUPERSEDED]` 機材・DUT、停止、再試験、事故対応、第三者影響と追加人員費をcurrency rangeで
  比較する旧案は採用しない。
- `[DESIGNED]` 契約・保険・法域が未確認なら法的賠償責任を`UNDETERMINED`とし、AIが推定しない。
- `[SUPERSEDED]` `RiskExposure`と`BenefitProjection`の定量表示案は、`RiskSignal`と`BenefitSignal`の
  順序メタ表記へ置き換えた。
- `[DESIGNED]` 高リスク・高ベネフィットを自動却下せず、人員・予算・checkのdecision packetへ変換する。
- `[DESIGNED]` 非専門者向け要約とエンジニア向け詳細を同じsnapshot IDで結ぶ二層UIとする。
- `[DESIGNED]` 管理側の応答はfund、staff、request changes、defer、decline with reasonとし、
  Dashboardから実機を開始しない。
- `[DESIGNED]` ExecutionRiskScoreとEvidenceValueScoreからversion付き日本語templateで一文ガイダンスを出す。
- `[DESIGNED]` risk 200/value 250、risk 180/value 100、risk 250+/value 50を受入例として固定した。
- `[DESIGNED]` 画面文を正本、TTSを同一message IDの任意派生出力とし、TTSへ実機権限を渡さない。
- `[DESIGNED]` 主対象はDev／Engineerではなく、技術根拠を金銭・日程・品質へ変換できていない決裁層とする。
- `[DESIGNED]` Engineer viewを根拠正本、Executive viewを同じsnapshotの意思決定翻訳として分離する。

## Claim Boundary

この記録はメタGUIの責務と入力境界を設計したことだけを主張する。係数式の妥当性、GUI実装、
人員配置の有効性、事故低減、安全性、規格適合を主張しない。

## 内観メモ

- `[POEM]` 回路図より予算表を先に読む偉い猫にも、いま人を呼ぶべきかだけは逃さず伝える。
  しかし猫向けの大きな数字を、現場の鍵にはしない。

## 次回TODO

- [ ] 状態snapshot schemaを設計する
- [ ] 色覚に依存しない最小wireframeを作る
- [ ] 係数式は実測runと運用レビュー後に別決定記録で確定する
- [x] `[SUPERSEDED]` currency付きRiskExposure schemaは実装しない
- [ ] BenefitProjection schemaと非金銭価値の単位を設計する
- [ ] decision packetの管理側・エンジニア側wireframeを対で作る
- [ ] decision packet IDによる管理側・現場側の往復schemaを設計する
- [ ] `ja-JP-cat-v0`のmessage routingをofflineテストへ落とす
- [ ] TTSのdeduplicate、rate limit、muteをpresentation runtimeで試験する
