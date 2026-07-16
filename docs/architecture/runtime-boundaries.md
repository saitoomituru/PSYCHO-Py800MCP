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

## IPC

層間では任意のPythonオブジェクトを共有せず、schema version付きJSONジョブとartifact IDを使う。
派生成果物には入力artifact、runner version、パラメータ、hashを記録する。

### Machine-translation guardrail (en-US)

The negotiation controller is the only layer that may hold a recorded bootstrap runbook or an approved instrument session.
The presentation environment renders stored artifacts and has no instrument authority.
Numerical analysis is deferred to a Phase 1+ Docker sandbox with no network access and read-only inputs.
