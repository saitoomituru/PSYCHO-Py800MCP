# 実行環境と責任境界

状態: `[REVIEW]`

## 構成

```text
AI / MCP client
      |
      v
Negotiation Controller venv
  - MCP service
  - BootstrapRunbook / ApprovalSession
  - MeasurementPlan / AbortPlan
  - Measurement Source Inbox metadata
  - Standards source provenance
  - Instrument transport
  - RunManifest / ArtifactStore
      |
      +---- artifact ID ----> Presentation venv
      |                         - static SVG/PNG
      |                         - no instrument access
      |
      `---- Phase 1+ --------> Analysis Docker sandbox
                                - NumPy / SciPy
                                - no network
                                - read-only input
```

## ネゴシエーション層の禁止事項

- 数理解析・描画ライブラリを直接importしない
- 任意SCPI文字列をMCP入力として通さない
- 記録済みBootstrapRunbookまたはApprovalSessionの外で計測器へ接続しない
- unknownを成功または許可へ変換しない
- 生波形全体をMCP応答へ埋め込まない

## プレゼンテーション層の禁止事項

- 計測器へ接続しない
- 実機IP、SCPI資格情報、ApprovalSession tokenを受け取らない
- 任意のローカルパスを開かない
- 原本を上書きしない
- ゲシュタルト係数や色表示から実機権限、承認、SCPIコマンドを生成しない

## 数理解析Dockerの将来契約

- `--network=none`
- 非root
- 入力成果物はread-only mount
- 出力ディレクトリのみwrite可能
- CPU、メモリ、実行時間を制限
- image digest、lockfile、コマンド、終了状態をRunManifestへ記録
- timeout、OOM、parser errorを成功扱いしない
- 利用許諾を確認できない規格本文を入力しない
- 入力した要求項目のsource ID、版、hash、許諾区分を出力へ残す

## 規格書パーサーの将来契約

GUIが用意するローカルのMeasurement Source Inboxだけを入力面にする。規格書原本はread-onlyで開き、
hash固定後、ネットワークなし・macro／script実行なしのパーサーサンドボックスへ渡す。OCRや抽出結果は
派生成果物として原本artifact IDへ結び付ける。投入フォルダーをリポジトリやMCPホストへ公開しない。

## GUIの将来契約

GUIはSeason 3で、測定計画、出典、規格版、観測不能項目、送信予定コマンド、承認粒度、TTL、
AbortPlanを人間へ提示する。plan hashへの明示承認前は測定を開始しない。

GUI中止後、ネゴシエーション層は新規操作を拒否し、事前承認済みの縮退操作と部分成果物の確定へ
移る。read-onlyのMCP成果物面は維持するが、読取要求を実機操作権限へ昇格させない。

## bootstrap実験とApprovalSession

Season 0の最初の既知IP・`*IDN?`実験だけは、GUIやApprovalSessionの完成を前提にしない。
人間が固定runbookを明示起動し、target、完全一致の送信byte、最大接続数、最大送信数、応答byte上限、
timeout、中止条件、runbook hashをappend-only記録へ残す。実装はrunbookにない入力を受け付けない。

このbootstrap権限は、状態照会の追加、波形取得、ネットワーク走査、retry、設定変更、物理接続指示へ
継承しない。query-only ApprovalSessionが実装・オフライン試験され次第、bootstrap経路を通常運用から外す。

AIがプローブ位置、接地、DUT接続、電圧範囲、probe倍率、結合、入力インピーダンスを提案・変更する
段階は別の物理リスク境界である。誤設定でADC入力限界を超える可能性があるため、この境界は
MeasurementPlanとStep承認が実装されるまでfail closedとする。

## 操作capabilityの分離

承認の比例原則、独立した人間GUI、local bench metadata、包括拒否禁止の正本は
[`authority-proportionality-and-local-trust.md`](authority-proportionality-and-local-trust.md)を参照する。

| capability | 例 | MeasurementPlan承認 |
|---|---|---|
| `ANALYZE_STORED` | 保存済みCSV／binaryのReplay、描画、FFT | 不要 |
| `READ_EXISTING` | 画面表示、取得済みbuffer、現在状態の照会 | 不要。ObservationContext内で反復可 |
| `READ_DESIGN` | KiCad、netlist、設計資料のread-only参照 | 不要。対象境界と出自を記録 |
| `MOVE_OBSERVER` | 非接触範囲内のcamera pan／tilt／zoom／focus | 不要。可動範囲とframe出自を記録 |
| `DATA_QUALITY_CHANGE` | 時間軸、既存artifactの切り出し | 安全承認は不要。変更と影響を記録 |
| `START_MEASUREMENT` | AIによるarm、single、run、再取得 | Dev Check＋Engineer Check＋plan承認が必要 |
| `INPUT_PATH_CHANGE` | 垂直感度、offset、倍率、結合、入力impedance、電流range | Dev Check＋Engineer Check＋plan承認が必要 |

コマンド名ではなく実際の副作用で分類する。時間軸コマンドが取得開始、再arm、buffer clearを伴う機種では
`DATA_QUALITY_CHANGE`ではなく`START_MEASUREMENT`として扱う。反対に保存済みartifactの解析は、
計測器セッションと切り離し、過去の測定計画が未登録でも解析可能にする。その場合も出自と既知の条件、
不足情報を残し、解析結果を新しい物理観測へ昇格させない。

人間がlxi-gui、ngscopeclient、vendor GUI、front panelを直接操作する経路へ、PSYCHOのAI ApprovalSessionを
横から強制しない。その操作が安全だと認証する意味ではなく、AI起動経路と人間直接操作経路を混同しない
ためである。PSYCHOへ結果を取り込む場合は、人間操作由来のartifact／snapshotとして記録する。

`START_MEASUREMENT`と`INPUT_PATH_CHANGE`の実行前には、設計想定範囲を確認したDev Checkと、現物で
設計超過電圧・電流、GND loop、leakage、接続点、probe倍率、接地を確認したEngineer Checkの両方を
同じplan hashへ結び付ける。対象点、DUT、配線、probe、GND、入力経路の変更で両確認を失効させる。

各操作は確認済みbaselineに対する`hazard_delta`を持つ。絶対スコアが低いことは許可根拠にならない。
`may_increase_exposure`または`unknown`なら二者確認側へ倒す。`neutral`を宣言できるのは、機種別の
副作用metadataで入力曝露、入力保護、接地条件を悪化させないと確認できる操作だけである。

## ObservationContext

ユーザーが対象機器、画面、artifact、camera、KiCad project等を観測対象として選択したread-only境界。
この境界内の読取は、人間が目視・閲覧できる情報をAIへ写す感覚面であり、readごとの承認を要求しない。
対象追加、任意pathへの逸脱、write、測定開始、buffer生成、入力経路変更はObservationContextに含めない。

カメラ移動は電気測定開始ではないため、設定済みの非接触可動範囲内なら`MOVE_OBSERVER`として扱う。
カメラ機構がDUT、probe、配線、GNDへ接触し得る、または照明・出力が対象へ影響し得る場合は
観測面から外し、`hazard_delta=unknown`として別計画へ戻す。

## Stakeholder Risk Projection

ネゴシエーション層は技術ゲートの状態、`hazard_delta`、check状態、plan hash、作業mode、必要人員を
署名対象の状態snapshotとして出力する。プレゼンテーション層はそのsnapshotだけから係数、状態語、
アイコン、説明カードを描画する。表示層からネゴシエーション層へ承認や操作を逆流させない。

観測読取は`OBSERVING`として表示し、AIが人間の数値転記を補助しているだけなら追加の作業リスクを
付与しない。自動検査を計画・開始する時点で、計画責任者、監査者、Dev Check、Engineer Check、
不足人員を表示する。係数の数値だけを保存せず、算出元snapshotと理由コードを結び付ける。

## IPC

層間では任意のPythonオブジェクトを共有せず、schema version付きJSONジョブとartifact IDを使う。
派生成果物には入力artifact、runner version、パラメータ、hashを記録する。

## 拒否の最小化

fail closedは危険なcapabilityへ局所適用する。`INPUT_PATH_CHANGE`がblockedでも`READ_EXISTING`、
`ANALYZE_STORED`、取得済み成果物の確定まで一括停止しない。block responseは具体的hazard、missing evidence、
解消手順、現在許可されるcapabilityを返す。一般的免責文やサービス提供者の責任回避をengineering controlの
代用品にしない。

### Machine-translation guardrail (en-US)

The negotiation controller is the only layer that may hold a recorded bootstrap runbook or an approved instrument session.
The presentation environment renders stored artifacts and has no instrument authority.
Numerical analysis is deferred to a Phase 1+ Docker sandbox with no network access and read-only inputs.
Approval is proportional to physical side effects; it does not apply to every read or to independent direct
human control merely because AI integration exists elsewhere.
