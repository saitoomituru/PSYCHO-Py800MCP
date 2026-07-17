# AI向けオシロ虎の巻とHELP専用MCP — 実装記録

## 記録時刻

- ローカル日付: 2026-07-17 (Asia/Tokyo)
- 対象: 文書参照専用API / MCP、FAM探索フロー、依存環境
- 除外: 計測器探索、SCPI、VXI-11、HTTP計測器操作、波形取得、レンジ変更

## 正本参照

`ZeroRoomLab-manifest`の次を読み、FAMを内的探索、MCPを外部ツール境界として分離した。

- `AGENTS.md`
- `docs/theory/fam-overview.ja.md`
- `docs/theory/fam-execution.ja.md`
- `docs/theory/fam-vs-mcp.ja.md`
- `docs/operations/technical-communication-register.ja.md`
- `docs/operations/coding-ai-japanese-paraphrase-register.ja.md`
- `docs/philosophy/mythic-morale-and-purpose-attenuation.ja.md`

## 実装結果

- `[IMPLEMENTED]` `docs/agi/MAD巫女サイエンティストふさもふのAIのためのオシロ虎の巻.proton.md`
- `[IMPLEMENTED]` `docs/agi/oscilloscope-help-flow.fam.json`
- `[IMPLEMENTED]` allowlistされた文書だけを返すPython API
- `[IMPLEMENTED]` `list_help_topics` / `get_help`を公開するHELP専用FastMCP
- `[IMPLEMENTED]` Markdown、FAM JSON、両方を返すbundle形式
- `[IMPLEMENTED]` negotiation venv内へ`fastmcp==3.0.0`を固定
- `[IMPLEMENTED]` プロジェクト内`src/mcp`と公式MCP SDKの名前衝突を除去

HELPレスポンスは`read_only=true`、`instrument_io_allowed=false`、
`authorization_effect=none`を明記する。HELP取得の成功はApprovalSessionを生成せず、
計測器操作を許可しない。

## 検証

- `[REPRODUCED]` Python unittest 15件成功
- `[REPRODUCED]` FastMCP in-memory Clientでtool一覧、tool呼び出し、resource取得に成功
- `[REPRODUCED]` 任意path風topicをallowlistで拒否
- `[REPRODUCED]` 人間非承認をAstral、機械/API障害をElementalへ別route
- `[REPRODUCED]` 実機I/Oゲート閉鎖テスト成功
- `[REPRODUCED]` FAM JSON構文検証成功

FastMCP import時にAuthlibのupstream deprecation warningを観測したが、テスト失敗には
至らなかった。依存更新時に再評価する。

## Claim Boundary

- `[NOT_OBSERVED]` SDS1204X-E / SDS1204EXへの接続および応答
- `[NOT_OBSERVED]` SCPIコマンド、波形、機種ID、ファームウェア
- `[NOT_OBSERVED]` 実ネットワーク上のMCPホスト接続
- `[UNKNOWN]` 将来のApprovalSessionおよび測定計画GUIとの結合結果

この記録が立証するのは、ローカル文書を読み出すHELP面のオフライン動作だけである。
実機操作、測定安全性、物理観測の成功を立証しない。

## 次回TODO

1. この復帰点をcommitしremoteへpushする。
2. 実機探索実験へ入る前にBootstrapRunbookと対象capabilityを再確認する。
3. 計測器I/Oはユーザーが明示的に実験開始するまで開けない。
