# 2026-06-21 設計初期化ノート

## セッション概要

PSYCHO-Py800MCPの設計思想・アーキテクチャ・初期ファイル群を確立。

## 確定した設計思想

### 責任の境界
- Claudeは「標的ネットTP3、Startを押してください」しか言わない
- SCPIコマンドはエッジ端末が発行する
- トリガーを引いた指が責任を持つ
- 波形が映らないのは執行官の腕の問題

### 安全設計
- ナラティブ安全ではなく証拠保全型安全
- 事故ゼロは不能という前提
- 安全KPIは現場オペレーターが所有
- LLMベンダー倫理観は使わない（物質世界に責任を持てないから）
- ユーザーが判断基準を明示設定し責任を引き受ける

### コントロール移譲
- リスクが高いほどユーザーに制御権を還元する
- IEC 61508 SIL思想と同一

### 自動化の範囲
- 初期セットアップ（プローブ当て・最初のStart）: 人間
- 回り出したら: 自動パラメータスイープ・ngspice照合可
- 「ハードあかん」が返ってきた時: 人間が確認

## 確定したアーキテクチャ

- **GUI**: PyQt6 常駐アプリ（Mac: メニューバー / Win: タスクトレイ）
- **MCP**: fastmcp
- **SCPI**: pyvisa / socket直接
- **波形処理**: NumPy / SciPy
- **音声**: eSpeak NG（シビュラっぽい無機質な機械音声）
- **証拠保全**: SQLite + HDF5

## 音声モード

- sibyla（シビュラ）: jp, speed=130, pitch=50 → 通常
- enforcer（執行官）: jp, speed=160, pitch=30 → 緊急
- en_sibyla: en, speed=120, pitch=50 → 英語
- silent: None

係数が上がるほど音声が変調・不安定化（SphereOS-synthesizerエンベロープ転用予定）

## SphereOS-synthesizerとの関係

- `HIPSTAR-IScompany/SphereOS-synthesizer` の lib/ （Python 100%）を転用予定
- エンベロープエンジン → 係数→音声パラメータ変換に使う
- OpenAI SDK依存部分（fold_vector）は捨て、Python純粋部分のみ使う
- Season 3で実装予定
- 研究ノートとして SE耳コピ用の甦生も並行検討

## 初期化したファイル

```
README.md
AGENTS.md
CLAUDE.md
docs/interface_spec.md
docs/safety_design.md
docs/gestalt_spec.md
notes/2026-06-21_design-init.md（このファイル）
```

## TODO Season 1

- [ ] `src/gui/app.py` — PyQt6 メニューバー常駐骨格
- [ ] `src/mcp/server.py` — fastmcp MCPサーバー骨格
- [ ] `src/engine/gestalt.py` — ゲシュタルト係数エンジン
- [ ] `src/audio/voice.py` — eSpeak NG統合
- [ ] `src/evidence/logger.py` — SQLite証拠保全
- [ ] `config/safety_profile.json` — サンプル安全プロファイル
- [ ] `requirements.txt`
- [ ] SIGLENT SDS1204X-E SCPI基本ブリッジ

## メモ

- Mac校正ループ: Macラインアウト→オシロで補正テーブル生成が音響域オシレーターとして使える
- ANRAN固定カメラ(RTSP)でオシロ画面を読むフォールバックも検討
- CCUSログとの統合で寺徳コンサル用途にも展開可能
- 「係数が高いほど声が崩れる」演出はSphereOSエンベロープで実装予定
