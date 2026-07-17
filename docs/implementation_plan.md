# PSYCHO-Py800MCP 実装・実験計画

状態: `[REVIEW]`  
主言語: 日本語  
英語ロケール: en-US（機械翻訳時の責任境界に必要な最小記述のみ）

## 1. 目的

PSYCHO-Py800MCPは、計測器をAIへ無条件に開放する仕組みではない。人間が確立した測定環境と
明示的な承認セッションの内側で、ネゴシエーション層が計測器、成果物、プレゼンテーション層、
将来の数理解析サンドボックスを調停するローカルファーストの計測器MCPである。

本計画ではPhaseとSeasonを別軸として扱う。

- **Phase:** 責任境界、実行権限、検証契約、証拠保全の成熟度
- **Season:** 手持ち実機による探索から抽象化・製品化へ進む実装順序

## 2. 状態語彙

| 状態 | 意味 |
|---|---|
| PLANNED | 計画済み。コードも実測も存在しない場合を含む |
| DESIGNED | 文書または契約が設計済み |
| IMPLEMENTED | コードが存在し、オフラインテストを通過 |
| HARDWARE_VERIFIED | 記録した実機・ファームウェア・条件で動作を観測 |
| REPRODUCED | 宣言した同条件または変更条件で再現確認済み |
| UNKNOWN | 未確認。安全ゲートでは通過扱いしない |
| FAILED | 試行したが成立しなかった |
| INCONCLUSIVE | 成功・失敗の判定材料が不足 |

### Machine-translation guardrail (en-US)

`DESIGNED`, `IMPLEMENTED`, `HARDWARE_VERIFIED`, and `REPRODUCED` are separate evidence states.
A result verified on one instrument and firmware does not establish support for every model.
`UNKNOWN` never grants permission. Physical actions remain inside the locally approved session.

## 3. 実行環境境界

### 3.1 ネゴシエーション層

独立venvで動作し、MCPサービス、ApprovalSession、計測器トランスポート、RunManifest、
ArtifactStore、ジョブ調停を担当する。NumPy、SciPy、Matplotlibを直接importしない。

### 3.2 プレゼンテーション層

別venvで動作し、保存済み成果物からSVG/PNG等を生成する。実機IP、SCPI接続、承認資格情報を
持たない。入力は任意パスではなくartifact IDと描画パラメータに限定する。

### 3.3 数理解析層

Phase 1以降にDockerサンドボックスを検討する。入力原本はread-only、出力先だけwrite可能、
ネットワークなし、非root、CPU・メモリ・時間制限付きとする。FFT、統計、フィッティング、
異常判定はこの層の責務であり、Season 0のネゴシエーション層へ混ぜない。

### 3.4 動的規格解決・測定計画

Season 3では、企画原本・規格原本・要求項目をユーザーがローカル環境へ投入する。システムは
原本を自動取得せず、公式メタデータで版・状態・発行者・更新有無だけをゼロトラストで照合する。
投入原本のAI解析権限を確認できない場合は推測せず`⊥`で停止し、ユーザーが抽出・承認した要求項目を
求める。利用可能な要求項目と数理層からMeasurementPlanを作り、GUIユーザーがplan hashを
承認するまで測定を開始しない。詳細は
[`architecture/measurement-plan-approval.md`](architecture/measurement-plan-approval.md)を参照。

GUIはユーザー環境にMeasurement Source Inboxを用意する。投入原本はread-onlyでhash固定し、
ネットワークなし・script／macro実行なしのパーサーサンドボックスで要求候補を抽出する。
フォルダー投入は計画承認ではなく、GUIで要求候補とplan hashを別途確認・承認する。

測定根拠は公的規格に限定しない。オープンサイエンス手順、オープンハードウェア開発基準、
ZeroRoomLab-manifest、ラボSOP、現場指示書、メーカー手順、契約要求、実験固有プロトコルを
MeasurementBasisBundleへ正規化する。Dev、characterization、pre-compliance、formal test supportを
区別し、「どの版のどのルールで測ったか」を全runへ保存する。

詳細は [`architecture/runtime-boundaries.md`](architecture/runtime-boundaries.md) を参照。

## 4. Phase計画

### Phase 0: 文書と責任境界

- 設計済み、実装済み、実機確認済みを分離する
- IEC 61508は「考え方を参照」と記し、適合を主張しない
- unknownをスコアではなく独立したfail-closedゲートにする
- bootstrap runbookと将来のApprovalSessionを分離し、対象機器、操作、上限、TTL、解除条件を定義する
- ZeroRoomLab-manifestの正本導線、800系一覧、remote URLを同期する
- 未存在ファイルを実装済みとして参照しない
- 実験ノートと生成果物の保存境界を確立する
- ネゴシエーション層とプレゼンテーション層のvenv境界を用意する

### Phase 1: 再生可能な解析契約

- 保存済み成果物だけでReplayできることを確認する
- 数理解析Dockerの入出力契約、資源制限、失敗状態を定義する
- 同じ成果物を複数runnerへ渡し、結果と環境差を記録する

### Phase 2: 承認付き物理操作

- AIが起動する測定開始、垂直レンジ系変更、RUN/STOP、連続取得をApprovalSessionへ結合する
- 時間軸等のdata-quality変更と、ADC保護に関わるvertical/input-path変更を別capabilityにする
- 中断、期限切れ、切断、部分応答、再接続、状態復元を試験する
- 証拠ログの改ざん検出と承認・操作の結合を強化する

### 承認機構の導入順序

承認機構が未実装なのにApprovalSessionを必須とすると、承認機構を検証する最初の通信まで永久に
開始できない。この循環を避けるため、権限を次の順序で導入する。

1. **offline:** 実機I/Oなし。承認不要
2. **bootstrap query-only:** 人間が固定runbookを明示起動する一回限りの実験権限
3. **query-only ApprovalSession:** 機械的なscope、TTL、回数上限、監査ログを実装
4. **data-quality control:** 時間軸等、物理破壊を増やさない変更を記録付きの独立capabilityとして追加
5. **measurement-start / input-path control:** AIによる測定開始と垂直レンジ系変更を二者確認付きで追加
6. **physical-plan approval:** AIがプロービング候補、入力レンジ、倍率、結合、インピーダンス、接地、
   DUT電源や信号源操作を提案する場合のPlan／Stage／Step承認

bootstrap query-onlyはApprovalSessionの代用品ではない。既知の固定IPへ、事前表示した完全一致byte列を
上限回数だけ送り、応答を有界に読む実験専用例外である。任意SCPI、探索範囲拡大、自動retry、設定変更、
物理接続の指示を許可しない。runbook hash、実験者の起動記録、送受信原本、終了状態を保存する。

物理的な主リスク境界は、AIがプローブ位置や接地を指示する時点、およびADC入力限界に関わる
電圧範囲、probe倍率、入力インピーダンス、結合を決める時点に置く。この境界より先は
ApprovalSessionとMeasurementPlanが未実装ならfail closedとし、人間の会話上の了承だけで迂回しない。

保存済み成果物のReplay、描画、数理解析にはMeasurementPlan承認を要求しない。ユーザーがすでに
プロービングと取得を成立させた計測器から既存結果を読む場合は、対象コマンドが取得開始、再arm、
buffer clear、設定変更を伴わないと確認できたときだけ`READ_EXISTING`に分類する。不明なら
`START_MEASUREMENT`へ倒す。

ユーザーが観測対象を選択した`ObservationContext`を設け、その範囲内の反復読取へ都度承認を要求しない。
対象には画面上の測定値、既存buffer、保存artifact、カメラframe、KiCad、netlist、設計資料を含められる。
これは実行権限ではなくread-only対象境界であり、対象ID、出自、読取時刻は証拠として記録する。
カメラのpan／tilt／zoom／focusは、設定済み非接触可動範囲内でDUT、probe、GND、入力経路、信号源を
動かさない場合だけ観測操作とする。物理接触や配線変化の可能性があれば`hazard_delta=unknown`へ戻す。

時間軸と既存artifact上の表示・切り出しは`DATA_QUALITY_CHANGE`とし、変更前後とデータへの影響を記録する。
時間軸操作が機種固有動作として取得開始や再armを伴う場合は例外なく`START_MEASUREMENT`へ再分類する。
垂直感度、垂直offset、probe倍率、AC/DC結合、入力インピーダンス、電流レンジ等は
`INPUT_PATH_CHANGE`とし、時間軸と同じ許可へ束ねない。

AIが`START_MEASUREMENT`または`INPUT_PATH_CHANGE`を実行するには次の二つを同じplan hashへ固定する。

- **Dev Check:** 設計上の期待電圧・電流、通常値、最大値、過渡、source impedance、許容入力範囲を確認
- **Engineer Check:** 現物のプローブ位置、倍率、接地、実電圧・電流の事前確認、設計超過、
  GND loop、leakage、絶縁状態を機械的に確認

どちらかが欠ける、期限切れ、対象点や配線が変わる、値が設計想定を超える場合は開始・レンジ変更を拒否する。

権限判定は絶対リスクスコアではなく、確認済みbaselineから提案操作への`hazard_delta`を使う。

- `none`: 保存artifact解析。実機状態へ影響しない
- `neutral`: 時間軸等、入力曝露を増やさないことが機種契約で確認済み
- `may_increase_exposure`: 感度側へのrange変更、50 ohm入力、倍率・結合・offset・接地変更、測定開始等
- `unknown`: 副作用またはbaselineが不明。`may_increase_exposure`と同じ承認側へ倒す

操作後の絶対スコアが低くても、baselineより破壊方向へ動くなら二者確認を要求する。逆に安全方向に見える
変更でも、vendor仕様と現在状態から単調に曝露が減ると証明できなければ`unknown`とする。

## 5. Season計画

### Season 0: 手持ち実機による探索ベンチ

最初の対象はSDS1204X-E。固定IPとTCP Socketを使い、人間が明示起動する固定bootstrap runbookから始める。
その観測を使ってquery-only ApprovalSessionの実装と試験へ進む。
VXI-11、mDNS/LXI、限定サブネット探索は固定IP縦切りの後に行う。

#### S0-A: query-only縦切り

1. 人間が物理接続とCH1表示を確認する
2. `*IDN?`で機種・シリアル・ファームウェアを観測する
3. 現在の時間軸、垂直軸、サンプルレート、メモリ深度等を照会する
4. 現在設定のままSCPI波形バイナリを取得する
5. 原本、状態、SCPI記録、manifest、hashをGit外へ保存する
6. プレゼンテーション層が保存済み成果物から静的プレビューを生成する

初回は`*RST`、Autoset、RUN/STOP、時間軸、垂直軸、トリガー、WFSUの変更を許可しない。
これはbootstrap runbookを最小化するためであり、将来の通常運用で時間軸を危険操作へ分類する意味ではない。

#### S0-B: 取得方式比較

- SocketとVXI-11
- SCPIバイナリとhost-generated CSV
- 計測器native CSVが取得できた場合は別原本として比較
- 点数、時間軸、振幅、欠落、補間、転送時間を記録

#### S0-C: MCPとReplay

- `discover_instruments`
- `identify_instrument`
- `capture_raw`
- `list_runs`
- `list_artifacts`
- `read_artifact_slice`
- `render_waveform_preview`

生データ全体をLLMへ返さない。パスを受け取らずrun IDとartifact IDで参照し、読み出し量を制限する。

#### S0-D: USB計測器探索

SDS縦切り後に、USB VID/PID、製品文字列、シリアル、インターフェース種別、既知ドライバー候補を
列挙する。製品名ではなく観測したUSB descriptorを正本にする。Season 0ではvendor control transfer、
ファームウェア投入、kernel extension導入を行わない。

### Season 1: 実測から抽象を固定

SDS、USB計測器、Replayの少なくとも3系統を比較し、次を設計する。

- InstrumentAdapter
- Transport
- RawArtifact / CanonicalTrace
- RunManifest / CapabilityManifest
- ArtifactStore
- ApprovalSession
- AnalysisJob / PresentationJob

### Season 2: 承認付き設定変更と連続測定

時間軸等のdata-quality変更を入力経路変更から分離し、二者確認付きの測定開始・垂直レンジ変更、
連続取得、限定スイープ、緊急停止、状態復元へ進む。Season 0で始めた証拠保存を、
承認と操作が追跡できるtamper-evidentな構造へ強化する。

### Season 3: 上位統合

GUIを人間の承認・中止面として実装し、動的規格解決、MeasurementPlan、承認粒度の選択、
部分データ確定、MCPホスト向けread-only成果物面を統合する。KiCad、Vision、ngspice、
リバースモード、自律スイープも扱うが、Season 0〜2の証拠なしに先行実装しない。

同じGUIへStakeholder Risk Dashboardを置く。技術非専門の管理、人事、出資、現場責任者へ、現在が
観測補助、解析、計画監査待ち、二者確認待ち、承認済み実行、高リスク作業、中止・縮退のどこかを
係数、状態語、アイコン、必要人員で示す。係数は技術ゲートの出力を圧縮するread-only projectionであり、
係数からApprovalSessionを生成したり、承認を推測したりしない。詳細は
[`architecture/stakeholder-risk-dashboard.md`](architecture/stakeholder-risk-dashboard.md)を参照。

Dashboardでは`DecisionRoleMap`、`RiskExposure`、`BenefitProjection`、`LegalLiabilityStatus`を分離する。
RiskExposureとBenefitProjectionはrange、根拠、confidenceを同じ画面で対にして表示する。
高リスク・高ベネフィットは却下へ直結させず、必要人員、予算、check、決定権限をdecision packetへまとめる。
法的責任は詳細情報とし、契約・保険・法域が不明なら`UNDETERMINED`にする。

承認済み計画は規格アップグレードで黙って変更しない。新版を検出した場合は、ユーザーへ新版原本または
更新要求項目の投入を依頼し、新しいSourceBundle、数理環境、plan hashを作って再承認を要求する。
GUI中止後は新規操作を止め、事前承認済みの
縮退操作、取得済み原本の部分確定、MCPホストへのread-only公開だけを行う。

GUIでは採用中のMeasurementBasisBundle、優先順位、衝突、逸脱、適用step、compliance intentを
表示する。公的規格とローカル指示のどちらを優先するかはユーザーが決め、AIは暗黙統合しない。

## 6. Season 0 bootstrap開始ゲート

- [ ] bootstrap query-only runbookの固定送信先、byte列、回数、応答上限、timeoutが文書化されている
- [ ] runbook hashと人間の明示起動を記録できる
- [ ] 生成果物のGit外保存先と公開用正規化先が分離されている
- [ ] ネゴシエーション層とプレゼンテーション層のvenvが分離されている
- [ ] Pythonバージョンとlock方針が記録されている
- [ ] 実機試験テンプレートが存在する
- [ ] 実験中止条件が明記されている
- [ ] 実験者が送信予定SCPIを確認している

本リポジトリの準備作業は、このゲートの直前まで進め、実機通信は人間が固定runbookを明示起動した後に
開始する。bootstrap実験から任意SCPIや物理プロービングへ権限を昇格させない。
