# notes/ 実験・監査記録ガイド

## 適用範囲

このファイルは`notes/`以下の実験記録、監査記録、引き継ぎログに適用する。
既存の`notes/`を正本棚として維持し、`note/`を並設してログを分裂させない。

## 正本参照

作業前にZeroRoomLab-manifestの次を確認する。

- `AGENTS.md`のEvidence Hierarchy、`unknown != pass`、FAMとMCPの責任分離
- `docs/operations/workspace-boundary-register.ja.md`
- `docs/operations/technical-communication-register.ja.md`
- `docs/operations/coding-ai-japanese-paraphrase-register.ja.md`
- `docs/operations/dotfiles-and-gitignore-policy.ja.md`
- `note/AGENTS.md`

manifestの記述から、本リポジトリの実装済み事実や実機動作を推測しない。

## 記録分類

- `EXPECTED`: 実験前の期待
- `OBSERVED`: 実機または原ログで観測
- `REPRODUCED`: 宣言した条件で再現確認済み
- `INFERRED`: 観測からの推論
- `PLANNED`: 未実装の計画
- `UNKNOWN`: 未確認
- `NOT_OBSERVED`: 観測器・取得項目が有効でなかった
- `FAILED`: 試行したが成立しなかった
- `INCONCLUSIVE`: 成否の判定材料が不足
- `DEVIATION`: 計画条件からの逸脱

必要に応じて`[FACT]`、`[HYPOTHESIS]`、`[POEM]`、`[LIMITED]`、`[NEEDS-REVISION]`、
`[Layer A]`等のmanifest側タグを併記する。

## 実機試験の必須項目

- 日時（UTCとローカル時刻）
- 検証範囲、対象、除外範囲
- ホスト環境とGit commit
- オペレーター／観測者
- 計測器ID、接続方式、ファームウェア
- 入力信号、プローブ、倍率、カップリング、接地
- 実行権限種別（BootstrapRunbook / ApprovalSession）、範囲、hash、期限
- 送信したコマンド
- 観測できた状態／観測できなかった状態
- 生成成果物、出自、hash
- 失敗、逸脱、中止理由
- Claim Boundary
- 内観メモ
- 次回TODO

## 禁止事項

- 未確認を成功扱いしない
- 計画を実装済み・実機確認済みと書かない
- 生ログを要約で上書きしない
- 過去の失敗記録を削除しない
- ベンダー固有観測を全機種共通仕様として断定しない
- IP、未匿名化シリアル、秘密値、生HDF5、生SQLiteを公開記録へ転記しない
- 事実、推論、内観メモを同じ段落へ混ぜない
