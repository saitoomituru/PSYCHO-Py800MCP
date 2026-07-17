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

PSYCHO-PASSの犯罪係数風に、現在の現場状態を技術非専門の管理者、人事、出資者にも一目で伝える
メタGUI表示。目的は安全判定の自動化ではなく、「いまは観測・数値ログ支援だけ」「次は自動検査なので
計画監査が必要」「ここからは高リスクなので増員」という運用状況の圧縮プレゼンテーションである。

この読み手には責任が金銭曝露として初めて届く場合があるため、Dashboardは役割名だけで終わらせない。
機材・DUT交換、停止時間、再試験、事故対応、第三者影響の概算rangeと根拠を表示し、追加人員の費用と
確認を省略した場合の曝露を並べる。ただしAIは法的賠償責任者を推定しない。契約、保険、法域、組織決裁が
未入力なら`LEGAL LIABILITY: UNDETERMINED`を明示し、技術担当者へ勝手に賠償責任を転嫁しない。

ユーザーがすでにプローブしている画面や値をAIが読む行為は、人間の目視・転記を補助する
`OBSERVING`として表示し、それ自体へ作業リスクを加算しない。自動検査、測定開始、入力経路変更では、
計画責任者、監査者、Dev Check、Engineer Check、必要人員、未確認事項を係数と同じ画面へ出す。

旧版の係数閾値と「即時執行可」という対応表は廃止予定で、実装権限へ使用しない。絶対スコアの
高低ではなく、人間が成立させた現在状態から次の操作が破壊方向へ倒れるかを`hazard_delta`として判定する。
AIによる測定開始または破壊方向・影響不明の入力経路変更には、設計想定範囲を確認するDev Checkと、
実際のプロービング対象を確認するEngineer Checkの両方を必要とする。

係数はプレゼンテーション用の派生値であり、低い値が操作を許可せず、高い値が自動的に操作を禁止する
わけでもない。実行可否は独立した技術ゲートが決める。係数表示には必ず状態語、根拠、必要な次の人員を
併記し、`UNKNOWN`を平均値へ埋めない。

> `[POEM]` 数式を読まない偉い猫にも、青なら観測、黄なら計画を見ろ、赤なら人を呼べ、と一秒で
> 伝えるための計器盤。ただし猫の肉球で安全ゲートは開かない。

> **en-US guardrail:** The Gestalt score is a stakeholder communication display, not a safety decision
> or authorization mechanism. It summarizes the current work mode, unresolved checks, responsible
> roles, staffing needs, and evidence-backed cost exposure. Technical gates remain authoritative,
> and the dashboard does not determine legal liability.

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

承認機構は危険度に合わせて段階導入する。最初の固定IP・query-only識別実験は、まだ存在しない
ApprovalSessionを前提にせず、人間が送信先、送信byte、回数、timeout、中止条件を固定したrunbookを
明示起動し、その記録を残す。AIによるプローブ位置の指示、DUT接続、入力レンジ・probe倍率・結合・
入力インピーダンスの決定、出力や装置状態の変更へ進む前には、機械的なApprovalSessionを必須にする。
現在の閉じた実験ゲートは、そのbootstrap実験実装が入るまで維持する。

ユーザーがすでにプローブと初回取得を成立させている場合、保存済み成果物の再生・描画・数理解析に
測定計画承認は要求しない。計測器から「すでに存在する取得結果」を読む操作も、取得開始、再arm、
設定変更を暗黙に伴わないことが機種契約で確認できればread-existingとして扱う。時間軸の変更は
物理破壊よりデータ品質へ影響する操作として記録付きで許可できるが、暗黙に測定開始するコマンドなら
start-measurementへ分類し直す。垂直レンジ、probe倍率、入力インピーダンス、結合、offset等は
ADC保護境界として時間軸と分離する。

`hazard_delta`は`none`、`neutral`、`may_increase_exposure`、`unknown`を持つ。`unknown`を低スコアへ
丸めず、`may_increase_exposure`と同じ承認側へ倒す。高いV/divへ変更する等、一見保護方向に見える操作も、
入力インピーダンスや結合、内部attenuatorの副作用を機種契約で確認できなければ安全側とは断定しない。

これは都度承認する読取ではない。ユーザーが観測対象を選んだ`ObservationContext`の内側では、オシロの
画面表示、既存buffer、カメラframe、KiCad／netlist／設計資料をAIが反復してread-only参照できる。
人間が目視している情報をAIが読むこと自体は`hazard_delta=none`である。将来のカメラ移動も、設定済みの
非接触可動範囲内でDUT、probe、接地、入力経路を動かさないなら観測操作として扱う。観測履歴は出自と
再現性のため記録するが、測定計画の承認記録へ偽装しない。

> **en-US guardrail:** The first known-target, query-only identification run may use a human-started,
> immutable bootstrap runbook before ApprovalSession exists. This exception never permits AI-directed
> probing, DUT connection, input-range decisions, state changes, or autonomous retries.
> Analysis of stored artifacts requires no measurement-plan approval. A time-axis-only change is a
> recorded data-quality operation; AI-initiated acquisition and vertical/input-path changes require
> both design-envelope and physical-probe checks plus an approved plan.

### Season 3の測定計画GUI

将来のGUIでは、企画原本・規格原本・要求項目をユーザーがローカル環境へ投入する。システムは
規格本文を自動取得せず、公式メタデータで版・状態・発行者・更新有無を照合し、利用を許可された
要求項目から数理層とMeasurementPlanを構築する。本プロジェクト自体の規格認証を目的にせず、
適用規格と正式な適合性判断はユーザーまたは必要な専門家へ返す。

GUIにはユーザー環境内の「測量規格書投入フォルダー」を用意する。投入原本は外部送信せず、
read-onlyでhash固定し、ネットワークとscript実行を持たないローカルパーサーで読む。フォルダーへの
投入は測定承認ではない。抽出された要求項目とMeasurementPlanを別画面で承認するまで実機操作しない。

投入できるのはPayToGete型の公的規格だけではない。本番規格測量前のDev段階では、
オープンサイエンスの実験手順、オープンハードウェア開発基準、ZeroRoomLab-manifest、各ラボのSOP、
各現場の指示書、メーカー手順、実験固有プロトコルもMeasurementBasisBundleとして扱う。
重要なのは肩書きの強さではなく、**どの版の、どのルールで、どのstepを測ったか**を残すこと。

複数ルールが衝突した場合、AIは勝手に混ぜない。GUIへ差分と適用範囲を返し、ユーザーが優先順位と
逸脱を承認する。Dev試験やpre-compliance結果を正式認証へ自動昇格させない。

plan hashへのユーザー承認がなければ測定を開始しない。途中中止時は新規操作を止め、事前承認済みの
安全停止、取得済みデータの部分確定、MCPホスト向けread-only成果物面へ縮退する。規格の新版を
検出しても承認済み計画を黙って変更せず、新しい計画として再承認を要求する。

> **en-US guardrail:** User-supplied source material, verified standards metadata, and user-authorized requirements may inform a measurement
> plan, but this project does not issue certification. A standards update requires a new plan and new
> approval. User cancellation blocks new instrument actions and finalizes only the data already obtained.
>
> Open-science protocols, open-hardware development profiles, project manifests, lab SOPs, site
> instructions, and manufacturer procedures are also valid planning inputs. Every run records exactly
> which versioned rules were selected, where they applied, and which deviations the user approved.

#### PayToGete

必要規格をシステムが自動取得する案は、規格本文の購入・利用許諾・AI利用条件が参入ゲートに
なっていたため変更した。ニートの財布に優しくないゲートを無理に破らず、権利を持つユーザーが
原本をローカル投入し、システムはその机の上で読む。

> 「安全はみんなのため」――ただし本文は決済後。
>
> PayToGeteは、ゼロトラストより先にカード番号を信じる。
>
> だからAIは規格を盗りに行かない。人が置いた原本を外へ出さず、測る前に計画を人へ返す。

> **en-US guardrail:** `PayToGete` is satire about access cost, not permission to bypass copyright,
> licensing, or formal conformity assessment.

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
