# 2026-07-17 Season 3 ローカル規格書と測定計画承認

状態: `[FACT]` `[Layer A]` `[LIMITED]`

## 検証範囲

- 対象: ユーザー投入の企画・規格原本からMeasurementPlanを作るSeason 3構想
- 対象: GUI承認粒度、中止縮退、MCPホスト向けread-only成果物面
- 対象: IEC/ISO公式サイト上の版情報・利用条件の確認
- 除外: GUI実装、規格書parser実装、規格本文取得、実機測定

## 観測事実

- `[OBSERVED]` IEC公式は規格出版物とWeb内容に著作権・利用条件があることを明示している。
- `[OBSERVED]` ISO公式はISOコンテンツのAI利用に明示的な制限を掲示している。
- `[OBSERVED]` 規格本文をシステムが自動取得する設計を採用しなかった。
- `[OBSERVED]` 企画原本、規格原本、要求項目はユーザーがGUIのローカル投入フォルダーへ置く方針にした。
- `[OBSERVED]` システム外部取得は公式メタデータによる版、状態、発行者、更新有無の照合に限定した。
- `[OBSERVED]` フォルダー投入、要求候補の採用、plan hash承認を別操作に分離した。
- `[OBSERVED]` GUI中止後は新規操作をblockし、事前承認済みの縮退操作、部分成果物確定、
  MCPホスト向けread-only公開へ移る状態機械を設計した。

## 設計判断

- `Measurement Source Inbox`はユーザー環境のローカルデータ領域に作る。
- 原本をread-onlyで開き、size、mtime、SHA-256、形式を固定する。
- parserはネットワークなし、macro／script実行なし、read-only入力で動かす。
- OCR・抽出結果は原本artifact IDへ結び付く派生成果物とする。
- 規格新版を検出しても承認済み計画を変更せず、ユーザーへ新版原本の再投入を依頼する。
- 本プロジェクトは規格認証や正式な適合性評価を発行しない。

## 方針転換理由

- `[FACT]` 対象規格の多くはオープンな機械可読本文ではなく、購入・許諾・AI利用条件を伴う。
- `[FACT]` 個人R&Dで規格本文の自動取得を前提にすると、費用とライセンスが実装前の障害になる。
- `[DECISION]` 規格本文をシステムが取りに行く案から、権利を持つユーザーが原本をローカル投入する案へ変更した。
- `[POEM]` このアクセス障壁を`PayToGete`と呼ぶ。安全の門は公共向け、本文の鍵穴はカード向け。

## 公式参照

- https://webstore.iec.ch/en/copyright
- https://webstore.iec.ch/en/terms-conditions
- https://www.iso.org/copyright.html

## 未観測・取得不能

- `[NOT_OBSERVED]` 実際の規格書原本は投入・解析していない。
- `[NOT_OBSERVED]` parser、OCR、数理Dockerの対応形式・性能は未検証。
- `[UNKNOWN]` 各規格・購入形態ごとの具体的なAI解析許諾は、原本投入時にユーザー確認が必要。

## Claim Boundary

この記録はSeason 3の責任境界と状態機械を文書化したことだけを主張する。規格本文の解釈、
測定計画の妥当性、適合性評価、GUI、parser、実機測定が成立したことを主張しない。

## 内観メモ

- `[POEM]` 規格をAIが勝手に狩りに行くのではなく、人間が机へ置いた原本を、その机から持ち出さずに
  一緒に読む構造になった。資料を置く、計画を読む、測ることを許す、の三つが別の指になる。
- `[POEM]` ニートの財布に厳しいPayToGeteを、無断突破ではなくローカル原本と人間承認で迂回する。

## 次回TODO

- [ ] SourceArtifactとUserPermissionDeclarationのschemaを設計する
- [ ] MeasurementPlan、ApprovalPolicy、AbortPlanのschemaを設計する
- [ ] GUI投入フォルダーのOS別ローカル保存先を決める
- [ ] parser sandboxの対応形式と脅威モデルを作成する
- [ ] Season 3へ進む前にSeason 0〜2の実測証拠を揃える
