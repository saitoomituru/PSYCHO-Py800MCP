# PSYCHO-Py800MCP
**AIに波形の眼を開眼させるMCPブリッジ**

> シビュラシステムは人の魂を測定した。  
> PSYCHO-Py800MCPは電気信号の魂を測定する。

Mac/Winメニューバー常駐のPythonアプリ。  
オシロスコープ・ロジアナ・WebCam・顕微鏡をMCPで統合し、  
AIがスケマティックを読んで波形の眼を持つ。

> **現在地:** 設計文書は確立済み、実装と実機検証はこれから開始する。
>
> 「設計済み」「実装済み」「実機確認済み」は別々に記録し、計画を動作実績として扱わない。

### Machine-translation guardrail (en-US)

This repository distinguishes **designed**, **implemented**, and **verified on physical hardware**.
Those labels are not interchangeable. Current hardware observations apply only to the recorded
instrument, firmware, connection, commands, artifacts, and test conditions. The MCP surface does
not authorize an AI client to bypass the local approval session or operate an instrument directly.

---

## 役割分担

### 人間がやること（測定環境の構築）

```
プローブを当てる
GNDクリップを取る
オシレーターを繋ぐ
最初のStartを押す
```

物理接触・装備選択・最初のトリガー判断は人間の領域。  
ゲシュタルト係数が装備選択を補助するが、引き金を引くのは人間。

### 将来の自動化目標（測定環境と承認セッション確立後）

```
測定環境が回り出したら全部やる。

パラメータスイープの自動実行
周波数スキャン・共振点探索
ngspiceシミュとの自動照合
スケマティック信頼度の反復更新
次の測定点の決定
補正テーブルの自動生成
異常検出・アラート発火
証拠保全ログの記録
```

**「プローブ当てたら寝ていい」はSeason 3へ向けた設計目標であり、現在の実装状態ではない。**

---

## ゲシュタルト係数

LLMの倫理判断ではなく、IEC 61508等の機能安全の考え方を参照するプロジェクト固有の定量リスク計算。
現時点で規格適合または認証取得を主張しない。
装備選択を「感覚」から「数値」に変える。

```
< 100   通常プローブ、即時執行可
100-299 差動プローブ推奨
300-399 差動プローブ必須＋高圧モード
400+    執行官2名体制、監視官承認必須
```

係数はスケマティック情報・測定履歴・信頼度スコアで動的に更新される。

---

## アーキテクチャ

```
Claude（自動開発ループの主体）
　↓ 係数計算・パラメータ決定・解析・次手
MCP（PSYCHO-Py800MCP）
　↓ SCPI / sigrok / OpenCV
SIGLENT SDS1204X-E・実機ハード
　↓ 波形データ / "device_not_responding"
NumPy解析 → Claude（次のループへ）
```

### ユーザーロール

| ロール | 担当 |
|--------|------|
| 監視官（デベロッパー） | Claude Codeでロジック・MCPからリモート操作・自動ループ監視 |
| 執行官（ハードエンジニア） | 実機にプローブ当て・初期Startを押す・「ハードあかん」時の現場確認 |

### 2つの動作モード

**フォワードモード** — KiCadスケマティック読み込み済み、係数が確定的  
**リバースモード** — 基板写真→Vision推定→信頼度スコア付き暫定スケマティック→測定で反復収束

---

## システム構成

```
┌─────────────────────────────────────────┐
│        PSYCHO-Py800MCP 常駐GUI           │
│   Mac: メニューバー / Win: タスクトレイ   │
├──────────────────────────────────────────┤
│ MCPサーバー層（fastmcp）                  │
│  計測器(SCPI/sigrok) │ 映像(WebCam/顕微鏡)│
│  スケマティック(KiCad)│ 校正(Mac lineout) │
├──────────────────────────────────────────┤
│ ゲシュタルト係数エンジン                  │
├──────────────────────────────────────────┤
│ 音声合成（eSpeak NG）                     │
│  sibyla / enforcer / EN / silent         │
├──────────────────────────────────────────┤
│ 証拠保全レイヤー（SQLite + HDF5）         │
└──────────────────────────────────────────┘
```

---

## 将来の自動開発ループ（Season 3構想）

```
基準波形確立（人間がセットアップ）
　↓
Claude「100Hzで取得」→ SCPI自動設定 → 波形取得
　↓
NumPy FFT解析 → 「共振点が見えた、前後スキャン」
　↓
自動パラメータスイープ
　↓
ngspiceシミュと照合 → 「C3の値が実機と違う」
　↓
スケマティック更新提案 → 人間承認
　↓
次の測定点へ（ループ）
```

### Mac校正ループ

```
Python → 既知サイン波出力（全周波数帯）
　↓ SCPI自動取得
NumPy → 補正カーブフィッティング
　↓
correction_table.json 生成・以降の測定に自動適用
```

Macラインアウトの歪みを差し引いた真の測定値が得られる。

---

## PhaseとSeason

Phaseは責任境界・検証契約の成熟度、Seasonは手持ち実機から始める探索と製品化の進行を表す。
両者を同じ進捗軸として扱わない。正本は [`docs/implementation_plan.md`](docs/implementation_plan.md)。

| 区分 | 状態 | 内容 |
|---|---|---|
| Phase 0 | 監査対応中 | 文書、責任境界、参照正本、実験ログの床張り |
| Season 0 | 実験準備中 | SDS1204X-Eで探索、識別、原本取得、再表示の縦切り |
| Season 1 | 設計予定 | 実測成果物からAdapter・Artifact・Capability等の抽象を固定 |
| Season 2 | 未着手 | 承認付き設定変更、連続測定、証拠保全の強化 |
| Season 3 | 構想 | KiCad、Vision、ngspice、自律スイープ |

現在の実機検証環境は、Hackintosh上のSDS1204X-Eおよび手持ちの小型USBオシロスコープ。
他社・他機種は寄贈または検証機材の提供を受けた範囲で順次対応する。対応表では
「設計済み」「実装済み」「実機確認済み」を別々に記録する。

### 実験前runtime

```bash
./scripts/bootstrap_runtime_envs.sh
./scripts/verify_pre_experiment.sh
```

Python 3.11のネゴシエーション層とプレゼンテーション層を別venvへ作る。Phase 0では
第三者依存、FastMCP、描画ライブラリ、SCPI通信を起動せず、実験ゲートが閉じていることだけを検証する。

### Season 3の測定計画GUI

将来のGUIでは、企画原本・規格原本・要求項目をユーザーがローカル環境へ投入する。システムは
規格本文を自動取得せず、公式メタデータで版・状態・発行者・更新有無を照合し、利用を許可された
要求項目から数理層とMeasurementPlanを構築する。本プロジェクト自体の規格認証を目的にせず、
適用規格と正式な適合性判断はユーザーまたは必要な専門家へ返す。

GUIにはユーザー環境内の「測量規格書投入フォルダー」を用意する。投入原本は外部送信せず、
read-onlyでhash固定し、ネットワークとscript実行を持たないローカルパーサーで読む。フォルダーへの
投入は測定承認ではない。抽出された要求項目とMeasurementPlanを別画面で承認するまで実機操作しない。

plan hashへのユーザー承認がなければ測定を開始しない。途中中止時は新規操作を止め、事前承認済みの
安全停止、取得済みデータの部分確定、MCPホスト向けread-only成果物面へ縮退する。規格の新版を
検出しても承認済み計画を黙って変更せず、新しい計画として再承認を要求する。

> **en-US guardrail:** User-supplied source material, verified standards metadata, and user-authorized requirements may inform a measurement
> plan, but this project does not issue certification. A standards update requires a new plan and new
> approval. User cancellation blocks new instrument actions and finalizes only the data already obtained.

---

## ディレクトリ構成

```
/src
  /gui        - PyQt6常駐アプリ（メニューバー/タスクトレイ・メインウィンドウ）
  /mcp        - fastmcp MCPサーバー（計測器・映像・スケマティック・校正ツール）
  /engine     - ゲシュタルト係数エンジン
  /audio      - eSpeak NG音声統合・SEパック
  /evidence   - 証拠保全レイヤー（SQLite・HDF5）
/docs
  interface_spec.md   - MCPツール定義・レイヤー間仕様
  gestalt_spec.md     - ゲシュタルト係数仕様
  safety_design.md    - 安全設計思想・責任構造
/notes        - 実験ノート・作業ログ（AIエージェント/人間共通）
/design       - UI設計・スクリーンショット
/tests
```

---

## _800シリーズ位置づけ

| 型番 | 役割 |
|------|------|
| OND800 | Pi5 NDIマルチカメラ（映像の眼） |
| SAO800 | Mac OBSプラグイン（映像の橋） |
| FAN800 | ESP32 BLEメッシュ（空間の神経） |
| **PSYCHO-Py800MCP** | **計測器MCP（波形の眼）** |

---

## 関連リポジトリ

- [`saitoomituru/OND800`](https://github.com/saitoomituru/OND800) — NDIカメラシステム
- [`saitoomituru/SAO800`](https://github.com/saitoomituru/SAO800) — Mac OBSプラグイン
- [`HIPSTAR-IScompany/SphereOS-synthesizer`](https://github.com/HIPSTAR-IScompany/SphereOS-synthesizer) — エンベロープエンジン転用元

---

## ライセンス

- ソフトウェア: Apache License 2.0
- 将来的なハードウェア設計(OSH): CERN-OHL-P v2（追加時に明記）

---

*ZeroRoomLab / 齋藤みつる*  
*設計思想: Sphere Architecture / FAM / IEC 61508の考え方を参照*
