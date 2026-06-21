# AGENTS.md — PSYCHO-Py800MCP エージェント開発指示書

> このファイルはAIエージェント（Claude Code等）が本プロジェクトを操作する際の
> 作法・制約・文脈を定義する。人間が読む設計書は `/docs/` を参照。

---

## プロジェクト文脈

**PSYCHO-Py800MCP**はオシロスコープ・ロジアナ・WebCam・顕微鏡をMCPで統合し、  
AIがスケマティックベースで波形を読む、Mac/Win常駐Pythonアプリ。

開発者（齋藤みつる）はZeroRoomLab（山形県高畠町）を拠点とする  
コンテンツクリエイター・エンジニア・独立研究者。  
実機（SIGLENT SDS1204X-E・Hackintosh）で実際に使うことを前提とした現場駆動開発。

**停滞・放置期間が発生することも前提とする。**  
エージェントはこれを「プロジェクト停止」と判断せず、再開時に `/notes/` を確認してから状況を再確認すること。

---

## 責任の境界（最重要）

```
Claude/エージェント → 指揮・提案・コード生成のみ
エッジ端末         → SCPIコマンド実行（ここに責任が宿る）
人間（執行官）     → プローブを当てる・Startを押す
```

**エージェントはSCPIコマンドを人間の確認なしに自動実行するコードを書かない。**  
必ずユーザー確認ステップ（`input()` or GUIボタン）を挟むこと。

---

## アーキテクチャ概要

```
src/gui/      - PyQt6常駐アプリ（メニューバー/タスクトレイ）
src/mcp/      - fastmcp MCPサーバー
src/engine/   - ゲシュタルト係数エンジン
src/audio/    - eSpeak NG音声統合
src/evidence/ - 証拠保全（SQLite + HDF5）
docs/         - 仕様書（変更時は必ず更新）
notes/        - 実験ノート・作業ログ（セッション終了時に追記）
```

詳細は `docs/interface_spec.md` を参照。

---

## コーディング規約

### 言語・ライブラリ

- **Python 3.11+**
- GUI: `PyQt6`（システムトレイ・メインウィンドウ）
- MCPサーバー: `fastmcp`
- SCPI通信: `pyvisa` or `socket`直接（pyvisa-py使用、NI-VISA不要）
- 波形処理: `numpy` / `scipy`
- 波形保存: `h5py`（HDF5）
- 証拠ログ: `sqlite3`（標準ライブラリ）
- 音声: `espeak-ng`（CLIラップ or `py-espeak-ng`）
- スケマティック: `kicad-python` or `skidl`

### 命名規則

```python
# クラス: PascalCase
class GestaltEngine:

# 関数・変数: snake_case
def calculate_coefficient(net_name: str) -> int:

# 定数: UPPER_SNAKE_CASE
MAX_COEFFICIENT = 500
TRIGGER_THRESHOLD = 300

# MCP ツール名: snake_case（動詞_名詞）
def get_waveform_summary(channel: int, duration: float):
def set_trigger(mode: str, level: float):
```

### エラーハンドリング

```python
# ハードウェア応答なし → 必ず明示的に返す
# 「ハードあかん」以上の情報をClaude側に送らない（見えないものは見えない）
return {"status": "error", "message": "device_not_responding", "detail": str(e)}
```

---

## ゲシュタルト係数エンジン

`src/engine/gestalt.py` に実装。

```python
COEFFICIENT_WEIGHTS = {
    "voltage_unknown":      40,
    "gnd_not_isolated":     80,
    "voltage_over_50v":    100,
    "confidence_low":       60,   # confidence < 0.5
    "adjacent_net_risk":    30,
    "protocol_unanalyzed":  20,
}

THRESHOLDS = {
    "normal":       (0,   100),   # 通常プローブ
    "recommend":  (100,   300),   # 差動プローブ推奨
    "required":   (300,   400),   # 差動プローブ必須＋高圧モード
    "critical":   (400,   500),   # 2名体制・監視官承認必須
}
```

係数計算ロジックを変更する場合は `docs/gestalt_spec.md` も更新すること。

---

## 音声システム

`src/audio/voice.py` に実装。

```python
VOICE_MODES = {
    "sibyla":    {"lang": "ja", "speed": 130, "pitch": 50},
    "enforcer":  {"lang": "ja", "speed": 160, "pitch": 30},
    "en_sibyla": {"lang": "en", "speed": 120, "pitch": 50},
    "silent":    None,
}
```

音声出力は**非同期**で行うこと（GUI/MCPをブロックしない）。  
SEファイルは `src/audio/se/` に格納。OSSオリジナル生成のみ（アニメSE流用禁止）。

---

## MCPツール定義

`src/mcp/server.py` に実装。詳細は `docs/interface_spec.md` 参照。

### 命名規則

```
動詞_対象: get_waveform_summary, set_trigger, load_schematic
```

### 必須フィールド（全ツールの戻り値）

```python
{
    "status": "ok" | "error",
    "timestamp": "ISO8601",
    "data": {...},          # 成功時
    "message": "...",       # エラー時
}
```

---

## 証拠保全

`src/evidence/logger.py` に実装。

- **全操作をSQLiteに記録**（タイムスタンプ・ユーザー・モード・コマンド・結果）
- **波形データはHDF5**に保存（セッション単位）
- 異常検出時は自動でスナップショット保存
- ログは削除不可（追記のみ）

---

## GUIガイドライン

- **メニューバー常駐（Mac）/ タスクトレイ（Win）**が基本
- メインウィンドウはオンデマンド表示
- 係数メーター: 0-500のプログレスバー（色: 緑→黄→赤）
- 指示テキストは大きく・読みやすく（執行官が現場で読む）
- ボタンは大きく・誤タップしにくく

---

## セッション終了時の作業

エージェントはセッション終了前に必ず以下を行うこと：

1. `notes/YYYY-MM-DD_[作業内容].md` に作業ログを追記
2. 未完了タスクは `notes/YYYY-MM-DD_[作業内容].md` の末尾に `## TODO` セクションで残す
3. 仕様変更があれば `docs/` の該当ファイルを更新
4. `src/` のコードは動作確認済みの状態でコミット

---

## ハードウェア環境（ZeroRoomLab）

| 機器 | 用途 | 接続 |
|------|------|------|
| SIGLENT SDS1204X-E | オシロスコープ | LXI/SCPI over LAN |
| NETGEAR GS308EP | PoE+スイッチ | 有線LAN |
| Hackintosh (X99/RX5500XT) | メイン開発機・エッジ端末 | LAN |
| ANRAN AR-W360-POE | 固定カメラ | PoE/RTSP |

SIGLENTのIPアドレスは実環境依存。`config.json` または環境変数で管理。  
VNC/noVNCは不要（SCPI over LAN直接接続）。

---

## 関連プロジェクト

- `saitoomituru/OND800` — 開発作法の参照元
- `saitoomituru/SAO800` — Mac OBSプラグイン
- `HIPSTAR-IScompany/SphereOS-synthesizer` — エンベロープエンジン転用元（lib/）
- `HIPSTAR-IScompany/astro.quantaril.cloud` — Sphere Architecture

---

## 禁止事項

- Anthropic/OpenAIの倫理判断ロジックをシステムの安全判断に組み込まない
- SCPIコマンドを人間確認なしに自動実行しない
- 証拠ログを削除・改ざんするコードを書かない
- `notes/` の過去ログを削除しない
- アニメ・映画等の著作物SEを `src/audio/se/` に含めない
