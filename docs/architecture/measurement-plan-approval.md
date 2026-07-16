# 動的規格解決・測定計画・GUI承認境界

状態: `[REVIEW]`  
対象: Season 3 GUI / ネゴシエーション層 / 数理解析層 / MCP成果物面

## 1. 目的

PSYCHO-Py800MCP自体にIEC 61508等の規格認証を付与することを目的としない。
ユーザーがその場で投入した企画原本・規格原本・要求項目と、用途、対象、法域、測量目的を起点に、
公式な版情報をゼロトラストで照合し、ローカル環境で測定計画を組み立てる。システムが規格本文を
自動取得して企画原本の代わりにしない。

測定計画はAIが勝手に執行する命令ではない。人間がプロービング、接地、装備、対象回路、
許容範囲、承認粒度を確認し、GUI上で計画hashへ明示承認した後にだけ実行可能になる。

### Machine-translation guardrail (en-US)

PSYCHO-Py800MCP is not a conformity-assessment or certification authority. It may assemble a
measurement plan from user-supplied source material and provenance-checked metadata. No measurement
starts without explicit GUI approval of the exact plan hash. A standards update never modifies an
approved plan silently; it requires a new plan and new approval.

## 2. 規格解決のゼロトラスト原則

### 2.0 GUIの測量規格書投入フォルダー

GUIはユーザー環境のローカルデータ領域に、設定可能な`Measurement Source Inbox`を一つ用意する。
規格書、企画原本、要求仕様はユーザーがこのフォルダーへ投入する。リポジトリ配下、クラウド同期先、
MCPホスト側へ原本を自動複製しない。

```text
Measurement Source Inbox (user-local)
  -> stable-file check
  -> file type / MIME / magic validation
  -> SHA-256 and source artifact ID
  -> read-only parser sandbox (no network, no script/macro execution)
  -> extracted requirement candidates with page/section provenance
  -> GUI user review
  -> MeasurementPlan draft
  -> separate plan-hash approval
```

投入フォルダーはユーザーが選択・変更できる。Downloads全体や任意の親ディレクトリを暗黙走査しない。
ファイル投入は「資料を解析候補として渡した」ことだけを意味し、本文の正しさ、適用規格の確定、
測定計画の承認、実機操作の許可を意味しない。

#### 原本の扱い

- 原本をread-onlyで開き、上書き・正規化保存しない
- 読取前後でsize、mtime、hashを確認し、変化した場合は`SOURCE_CHANGED`で中断する
- 拡張子ではなくfile signatureも検証する
- PDF内スクリプト、添付実行物、外部リンク、Office macro等を実行しない
- パーサーはネットワークなし・read-only入力・制限付き一時出力で動かす
- OCR、テキスト抽出、ページ画像は派生成果物として原本hashへ結び付ける
- 走査画像、破損、暗号化、未知形式、抽出信頼度不足は`NEEDS_INPUT`へ返す
- 原本byte列をMCP応答へ載せない
- ファイルが差し替わった場合は新しいsource artifactとplan hashを作る

### 2.1 ユーザー指示を起点にする

- バックグラウンドで規格本文を無差別収集しない
- 企画原本、規格原本、測定要求はユーザーがGUIのローカル投入フォルダーへ置く
- ユーザーが用途、法域、規格番号、版、測定目的、必要な結果を提示する
- システムは投入原本のhash、ファイル種別、版表示、投入時刻を記録する
- ユーザーは、その原本をローカルの数理層・AIへ解析させる権限があるかを宣言する
- 規格番号が曖昧な場合は候補と根拠を返し、ユーザー選択まで計画を確定しない
- 適用規格の法的・契約的な最終判断をAIへ委譲しない

### 2.2 SourceBundle

測定計画に使用する各資料について次を固定する。

```json
{
  "publisher": "IEC",
  "document_id": "IEC 61508-1",
  "edition": "2.0",
  "publication_date": "2010-04-30",
  "lifecycle_status": "valid",
  "jurisdiction": "user_declared",
  "source_url": "official publisher URL",
  "retrieved_at": "ISO8601",
  "content_class": "user_supplied_source",
  "content_hash": null,
  "ai_use_allowed": "user_declared",
  "evidence": []
}
```

`content_class`は少なくとも次を区別する。

- `official_metadata`: 発行者、版、状態、日付等の公式公開メタデータ
- `public_normative_text`: 法令等、利用条件を確認できた公開本文
- `user_supplied_source`: ユーザーがローカル環境へ投入した企画・規格原本
- `licensed_machine_readable`: ユーザーがAI・ソフトウェア利用許諾を確認して投入した資料
- `user_curated_requirements`: ユーザーが権利と責任を確認して入力した要求項目
- `reference_only`: 存在と版は確認できるが、本文を数理層へ投入できない資料
- `unknown_rights`: 利用条件未確認。計画生成には使わない

### 2.3 著作権・利用許諾境界

- システム側からIEC/ISO等の有償規格本文を自動取得しない
- ユーザー投入原本であっても、許諾確認なしにLLM投入・数理解析しない
- 公開メタデータの確認と、規格本文のAI利用を同一視しない
- ローカルに購入済みPDFが存在しても、購入した事実だけではAI投入許可とみなさない
- 使用可能なのは、利用条件が許す公開本文、ユーザーが解析許可を宣言した投入原本、許諾済み
  機械可読資料、またはユーザーが権利確認のうえ抽出・承認した測定要求である
- 本文へアクセスできない、または利用条件が不明な場合は`UNKNOWN`／`⊥`で停止し、
  ユーザーへ必要資料または要求項目の提示を依頼する
- 規格本文をリポジトリ、RunArtifact、MCP応答へ無断転載しない

## 3. 規格アップグレード

新しい測定計画を作成するたびに、ユーザー投入原本に記載された規格の公式メタデータを取得し、前回の
SourceBundleと比較する。新版、追補、正誤票、廃止、置換候補を検出した場合は
`STANDARD_UPDATE_DETECTED`として提示する。

すでに承認された計画は、その計画が参照した版と要求項目のsnapshotを保持する。
新版検出によって実行中または承認済み計画を黙って変更しない。新版を採用する場合は、ユーザーへ
新版原本または更新要求項目の投入を依頼する。投入後に測定項目、数理環境、承認粒度を再構築し、
新しいplan hashへ再承認を要求する。

## 4. MeasurementPlan

測定計画には少なくとも次を含める。

- plan ID / schema version / plan hash
- ユーザー投入原本のartifact ID、hash、解析許可宣言
- パーサー、OCR、抽出環境、派生成果物、ページ／節provenance
- ユーザーが宣言した目的、用途、法域、対象DUT、除外範囲
- SourceBundleと採用した要求項目の出典
- 計測器、firmware、probe、attenuation、接地、入力限界、校正状態
- 観測可能項目と観測不能項目
- 測定点、プロービング手順、各stepの期待値と中止条件
- 送信予定コマンドと、設定変更／取得／解析の分類
- サンプリング、帯域、時間軸、測定不確かさ、必要な反復数
- 数理解析runner、image digest、lockfile、入力・出力schema
- 成果物、保持期間、MCPホストへ公開可能な粒度
- ApprovalPolicy
- AbortPlan / PartialFinalizePolicy

計画生成時に不足項目を推測で埋めない。欠落は`NEEDS_INPUT`としてユーザーへ返す。

## 5. 承認粒度

承認粒度は規格名だけで固定せず、ユーザー指示、物理リスク、操作能力、計画変更可能性から
MeasurementPlanごとに決める。最低限、次の階層を提示する。

### Plan承認

全測定で必須。plan hash、SourceBundle hash、instrument capability snapshot、TTL、AbortPlanへ承認する。
計画の重要項目が変わった場合は承認を失効させる。

### Stage承認

同一の物理接続・上限・コマンド分類内で複数stepをまとめる。低リスクの反復取得等で候補になる。

### Step承認

次の場合は原則としてstepごとの承認候補にする。

- プローブ位置、GND、DUT電源、回路トポロジーが変わる
- 電圧・電流・帯域・入力インピーダンス・probe倍率の上限が変わる
- RUN/STOP、出力、トリガー等、装置状態を変更する
- 規格要求または機器能力が`UNKNOWN`
- ユーザーがstep承認を要求した

### Query-only承認

機種識別や状態照会だけを許可する独立scope。設定変更、取得開始、連続測定へ昇格しない。

## 6. GUI状態機械

```text
DRAFT
  -> RESOLVING_SOURCES
  -> NEEDS_INPUT | READY_FOR_APPROVAL
  -> APPROVED
  -> RUNNING
  -> COMPLETED

RUNNING
  -> STOP_REQUESTED
  -> SAFE_STOPPING
  -> FINALIZING_PARTIAL
  -> ABORTED_PARTIAL

any state
  -> FAILED | BLOCKED
```

`APPROVED`へ到達していない計画は測定を開始できない。承認はユーザー、plan hash、scope、TTL、
承認時刻を持つ。期限切れ、機器差替え、probe変更、規格版変更、重要パラメータ変更で失効する。

## 7. 測定中止

GUIユーザーが中止を入力した時点で、ネゴシエーション層は新規測定stepと新規設定変更を拒否する。
中止後に許可されるのは、MeasurementPlanのAbortPlanで事前承認された縮退操作だけである。

1. `STOP_REQUESTED`をappend-onlyログへ記録
2. 新規操作をblock
3. 実行中コマンドをbounded wait、取消可能なら取消
4. 事前承認済みの安全停止・接続解放だけを実行
5. 取得済み原本を上書きせずhash確定
6. 未取得stepを`NOT_OBSERVED`、部分データを`PARTIAL`として記録
7. `ABORTED_PARTIAL` RunManifestを生成
8. MCPホスト側から成果物をread-onlyで取得可能にする

中止後に不足データを取り直したり、新しい解析条件で測定を継続したりしない。別planとして再承認する。

## 8. MCPホストへの成果物面

測定制御とデータ吸い上げを別capabilityにする。中止後もread-only成果物面は利用できる。

- `get_measurement_plan`
- `get_plan_status`
- `list_runs`
- `get_run_manifest`
- `list_artifacts`
- `get_artifact_metadata`
- `read_artifact_slice`
- `get_partial_summary`

任意パス、生ログ全体、規格本文、承認tokenを返さない。artifact ID、上限付きslice、hash、出自、
完全／部分／中止状態を返す。MCPホストからの読取要求は実機操作権限へ昇格しない。

## 9. 責任境界

- システム: 出典、版、利用条件、欠落、計画、コマンド、成果物、状態遷移を記録する
- 数理層: 許可された要求項目と保存済み成果物から候補計画・解析を生成する
- GUIユーザー: 適用規格、物理接続、承認粒度、プロービング、開始、中止を決定する
- 認証機関・有資格者: 必要な場合の正式な適合性評価を担当する。本システムは代替しない

## 10. 利用条件の公式参照

- [IEC Copyright](https://webstore.iec.ch/en/copyright)
- [IEC Webstore Terms and Conditions](https://webstore.iec.ch/en/terms-conditions)
- [ISO Copyright](https://www.iso.org/copyright.html)

利用条件は変更されうるため、リンク先を固定解釈せず、企画原本投入時とMeasurementPlan生成時に
ユーザーが現在の条件を確認する。リポジトリへ規格本文や許諾対象外の抜粋を複製しない。
