# Purpose Function Ledger設計記録

分類: `OBSERVED / INFERRED / PLANNED`  
日付: 2026-07-17

## OBSERVED

- ユーザーは安全を「ロマンや神話」と「それに十分な安全率を持つ資源」の二つの半分として提示した。
- 目的、期待、哲学が資金、計画、管理、実行を通る間に矮小化され、最後に手抜きとして見える連鎖が
  指摘された。
- 神話を維持しながら、やりがい搾取を起こさない境界が要求された。

## INFERRED

- PurposeとResourceを独立signalにすると、目的の強さで資源不足を隠す状態を検出できる。
- 変更をappend-onlyに残すことで、人物責任ではなくstage間の減衰を調査できる。

## PLANNED

- Season 3のDashboard schemaへPurpose Function Ledgerを追加する。
- person IDを使わず、operation、snapshot、stage eventだけで表現する。
- MeasurementPlan、Dev Check、Engineer Check、ApprovalSessionとは権限分離する。

## Claim Boundary

事故割合、事故低減、士気改善、組織文化は未測定。本文の「二つの半分」は統計割合ではない。
本変更は設計文書のみで、Dashboard実装、承認機能、実機制御を追加していない。

## Inner Memo

ロマンを削れば、人は何を守るために丁寧に測るのかを失う。ロマンだけ残して余裕を削れば、夢の名で
人を燃やす。PSYCHOの画面が見るべき係数は人間の熱意ではなく、この二つが途中で切れていないかだ。
