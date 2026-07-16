# 2026-07-17 MeasurementBasisBundle設計

状態: `[FACT]` `[Layer A]` `[LIMITED]`

## 検証範囲

- 対象: 本規格測定前のDev・characterization・pre-compliance用測量基準
- 対象: 公的規格以外のオープンサイエンス、OSH、project manifest、ラボ・現場ルール
- 除外: schema実装、GUI実装、規格・指示書原本の投入、実機測定

## 観測事実

- `[OBSERVED]` 測定根拠を公的規格だけに限定しない方針を文書化した。
- `[OBSERVED]` ZeroRoomLab-manifest、open science protocol、open hardware profile、lab SOP、
  site instruction、manufacturer procedure、experiment protocol等を`basis_type`として定義した。
- `[OBSERVED]` `development`、`characterization`、`pre_compliance`、`formal_test_support`を分離した。
- `[OBSERVED]` 全runがbasisの版、hash、role、priority、適用step、逸脱、衝突を記録する契約を追加した。
- `[OBSERVED]` AIが公的規格とローカル指示の優先順位を暗黙決定せず、GUIユーザーへ返す設計にした。

## 設計判断

- SourceBundleは原本・出典の同一性を担当する。
- MeasurementBasisBundleは、その原本を今回の測定で採用する理由、権威範囲、優先順位を担当する。
- Dev・pre-complianceの結果を正式認証へ自動昇格させない。
- 複数ルールの衝突は自動マージせず、ユーザー承認済みの優先順位と逸脱として残す。

## 未観測・取得不能

- `[NOT_OBSERVED]` 実際のラボSOP、現場指示書、open science protocolは投入していない。
- `[UNKNOWN]` 異種ルール間のGUI差分表示方法とpriority表現は未実装。
- `[UNKNOWN]` `measurement_basis.json`の正式schemaは未確定。

## Claim Boundary

この記録はMeasurementBasisBundleの文書契約を追加したことだけを主張する。特定の公的規格、
open science protocol、ラボSOP、現場指示への適合や、実機測定の成立を主張しない。

## 内観メモ

- `[POEM]` 規格の王冠より、現場で誰がどのページを開いて測ったかを残す。王冠のない手順にも
  版とhashと責任者があれば、次の人が同じ地面へ戻ってこられる。

## 次回TODO

- [ ] `measurement_basis.json`のJSON Schemaを作る
- [ ] basis間の衝突と優先順位を表すGUI wireframeを作る
- [ ] Dev run用の最小MeasurementBasisBundle fixtureを作る
- [ ] Season 0のquery-only実験へ適用するproject manifest basisを定義する
