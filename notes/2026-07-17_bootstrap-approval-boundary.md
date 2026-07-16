# 2026-07-17 bootstrap実験と承認機構の導入境界

状態: `[DESIGNED]` `[Layer A]` `[LIMITED]`

## 検証範囲

- 対象: 最初のネットワーク識別実験と将来のApprovalSessionの循環依存解消
- 対象: AIプロービング指示とADC入力限界に関わる物理リスク境界
- 除外: 実機通信、SCPI応答、波形取得、設定変更、物理接続変更

## 観測事実

- `[OBSERVED]` 現在のコードはApprovalSession未確立を理由に実機I/Oを拒否する。
- `[OBSERVED]` ApprovalSessionとGUIはまだ実装済みではない。
- `[OBSERVED]` 本変更では実機へ接続していない。

## 設計判断

- `[DESIGNED]` 最初の既知IP・`*IDN?`は、人間が固定BootstrapRunbookを明示起動する一回限りの
  query-only実験として分離する。
- `[DESIGNED]` BootstrapRunbookはtarget、完全一致byte、接続／送信回数、応答上限、timeout、
  中止条件、hashを固定し、任意SCPIと自動retryを許可しない。
- `[DESIGNED]` 観測結果を使ってquery-only ApprovalSessionを実装し、以後の通常経路とする。
- `[DESIGNED]` AIがプローブ位置、接地、DUT接続、入力レンジ、probe倍率、結合、入力インピーダンスを
  提案する段階は、MeasurementPlanとStep承認なしに進まない。
- `[DESIGNED]` 機器・probeの定格、想定最大電圧、過渡、接続点、GND基準のいずれかが不明なら
  `UNKNOWN`で停止する。ADC保護をスコアの平均で相殺しない。

## Claim Boundary

この記録は承認機構の導入順序と物理リスク境界を設計したことだけを主張する。BootstrapRunbook、
ApprovalSession、MeasurementPlan GUIの実装、SDS1204X-Eとの通信成立、安全性確認を主張しない。

## 内観メモ

- `[POEM]` 鍵を作るための部屋へ入る鍵がない、という循環は、細い検査窓を一本だけ先に作れば解ける。
  ただし窓から腕を伸ばしてプローブを動かせるようにはしない。

## 次回TODO

- [ ] S0-A0固定BootstrapRunbookを文書化する
- [ ] runbook parserとoffline拒否テストを実装する
- [ ] 実験者へ送信byteと中止条件を提示し、明示起動前で停止する
- [ ] bootstrap観測後、query-only ApprovalSession契約を実装する
