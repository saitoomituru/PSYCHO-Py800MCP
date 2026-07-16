# 実行環境と責任境界

状態: `[REVIEW]`

## 構成

```text
AI / MCP client
      |
      v
Negotiation Controller venv
  - MCP service
  - ApprovalSession
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
- ApprovalSession外で計測器へ接続しない
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

## IPC

層間では任意のPythonオブジェクトを共有せず、schema version付きJSONジョブとartifact IDを使う。
派生成果物には入力artifact、runner version、パラメータ、hashを記録する。

### Machine-translation guardrail (en-US)

The negotiation controller is the only layer that may hold an approved instrument session.
The presentation environment renders stored artifacts and has no instrument authority.
Numerical analysis is deferred to a Phase 1+ Docker sandbox with no network access and read-only inputs.
