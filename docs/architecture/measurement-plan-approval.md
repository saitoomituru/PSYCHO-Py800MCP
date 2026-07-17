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

## 1.1 方針転換理由: PayToGete

当初は、必要規格をシステムが都度公式から取得し、数理層と測定計画を構築する案だった。
しかし対象規格の多くはオープンな機械可読本文ではなく、購入、利用許諾、AI利用制限を伴う。
安全規格への入口そのものに費用と契約のゲートがあり、個人R&Dが本文の自動取得を前提にすると、
技術実装より先に財布とライセンスが単一障害点になる。

そこで、規格・企画原本は権利を持つユーザーがローカル投入し、PSYCHO-Py800MCPはその原本を
外へ持ち出さず、公式メタデータとの照合、測定計画化、承認、中止、証拠化を担当する方針へ変更した。

> 安全はみんなのため、と門には書いてある。
>
> 門番は言う、「本文は決済後です」。
>
> PayToGete――ゼロトラストより先に、カード番号を信じるゲート。
>
> ニートの財布に優しくないなら、原本は持っている人に持ってきてもらう。
>
> AIは奪わない。外へ投げない。その机で読み、測る前に人へ返す。

> **en-US guardrail:** `PayToGete` is satire about the cost and licensing barrier to standards access.
> It does not claim that copyright, licensing terms, or conformity requirements may be bypassed.

### Machine-translation guardrail (en-US)

PSYCHO-Py800MCP is not a conformity-assessment or certification authority. It may assemble a
measurement plan from user-supplied source material and provenance-checked metadata. No measurement
starts without explicit GUI approval of the exact plan hash. A standards update never modifies an
approved plan silently; it requires a new plan and new approval.

## 2. 規格解決のゼロトラスト原則

### 2.1 公的規格だけを入口にしない

MeasurementPlanは、PayToGete型の公的・有償規格だけを根拠にしない。本番の規格測定へ進む前の
Dev段階では、オープンサイエンスの再現手順、オープンハードウェア開発基準、ZeroRoomLab-manifest、
各ラボのSOP、各現場の指示書、メーカー手順、実験固有プロトコルも測量基準になりうる。

システムが「公的規格だから常に上位」「ローカル指示だから常に下位」と自動判断しない。
ユーザーが今回の目的、法域、契約、現場責任に対して各資料の役割と優先順位を宣言する。
衝突がある場合は自動マージせず、差分、適用範囲、未解決点をGUIへ返す。

### 2.2 GUIの測量規格書投入フォルダー

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

### 2.3 ユーザー指示を起点にする

- バックグラウンドで規格本文を無差別収集しない
- 企画原本、規格原本、測定要求はユーザーがGUIのローカル投入フォルダーへ置く
- ユーザーが用途、法域、規格番号、版、測定目的、必要な結果を提示する
- システムは投入原本のhash、ファイル種別、版表示、投入時刻を記録する
- ユーザーは、その原本をローカルの数理層・AIへ解析させる権限があるかを宣言する
- 規格番号が曖昧な場合は候補と根拠を返し、ユーザー選択まで計画を確定しない
- 適用規格の法的・契約的な最終判断をAIへ委譲しない

### 2.4 SourceBundle

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

## 2.5 MeasurementBasisBundle

投入資料が「何の権威を持つか」と「今回どの役割で使うか」をSourceBundleとは別に記録する。
SourceBundleは原本と出典の同一性、MeasurementBasisBundleは測定計画における採用理由と責任を扱う。

```json
{
  "basis_id": "basis_xxx",
  "basis_type": "lab_sop",
  "title": "計測ベンチ運用手順",
  "issuer": "user_declared_lab",
  "version": "2026-07-17",
  "effective_date": "2026-07-17",
  "source_artifact_id": "source_xxx",
  "source_hash": "sha256:...",
  "license_or_access": "user_declared",
  "authority_scope": "development_bench_only",
  "rule_role": "developmental",
  "compliance_intent": "development",
  "selected_by": "gui_user",
  "priority": 20,
  "deviations": [],
  "unresolved_conflicts": []
}
```

### basis_type

- `official_standard`: 法令・公的規格・業界規格
- `open_science_protocol`: 公開された実験・再現・測量プロトコル
- `open_hardware_profile`: OSH開発、bring-up、検証、相互運用基準
- `project_manifest`: ZeroRoomLab-manifest等のプロジェクト正本・責任境界
- `lab_sop`: ラボ固有の標準作業手順
- `site_instruction`: 工場、建設、撮影、保守等の現場指示書
- `manufacturer_procedure`: 機器メーカーのmanual、application note、校正・操作手順
- `contractual_requirement`: 顧客・委託・納入上の要求
- `experiment_protocol`: 今回の実験専用にユーザーが定めた手順
- `historical_baseline`: 旧試験や過去runを比較基準として使う場合

### rule_role

- `normative`: 今回の測定で必須として採用
- `contractual`: 契約・納入条件として採用
- `local_authority`: ラボまたは現場の執行ルール
- `developmental`: 本規格測定前のDev・bring-up基準
- `reference`: 参考比較。合否判定には使わない

### compliance_intent

- `development`: 回路・機器・取得経路を開発中に確認
- `characterization`: 性能・癖・限界を観測
- `pre_compliance`: 正式試験前の事前確認
- `formal_test_support`: 正式試験の補助記録。認証そのものではない

`development`または`pre_compliance`の結果を、正式な規格適合や認証取得へ自動昇格させない。

### 2.6 著作権・利用許諾境界

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
- MeasurementBasisBundle、採用優先順位、衝突、逸脱、compliance intent
- 計測器、firmware、probe、attenuation、接地、入力限界、校正状態
- 観測可能項目と観測不能項目
- 測定点、プロービング手順、各stepの期待値と中止条件
- 送信予定コマンドと、設定変更／取得／解析の分類
- サンプリング、帯域、時間軸、測定不確かさ、必要な反復数
- 数理解析runner、image digest、lockfile、入力・出力schema
- 成果物、保持期間、MCPホストへ公開可能な粒度
- ApprovalPolicy
- Dev Check（設計想定範囲、最大値、過渡、source impedance、許容入力）
- Engineer Check（実接続、実電圧・電流、設計超過、GND loop、leakage、絶縁、probe倍率）
- baseline stateと各操作のhazard delta
- PhysicalExposureEnvelope / ObservationWindowPolicy / OptimizationEnvelope
- AnomalyContract（異常定義、停止順序、証拠退避、定義外fallback）
- AbortPlan / PartialFinalizePolicy

計画生成時に不足項目を推測で埋めない。欠落は`NEEDS_INPUT`としてユーザーへ返す。

## 4.1 「どのルールでやったか」の固定

全runは`measurement_basis.json`を持ち、採用した全basisのID、version、hash、role、priority、
適用step、逸脱理由を保存する。GUIとMCP成果物面では、最低限次を回答できなければならない。

- この測定はどのルールに基づいたか
- そのルールを誰が選択したか
- どの版・hashを使ったか
- どのstepへ適用したか
- どの要求を満たした／満たせなかった／観測できなかったか
- 複数ルールが衝突した場合、誰がどの優先順位を承認したか
- どこを逸脱し、その理由と影響範囲は何か

公開記録では原本そのものを転載せず、公開可能なbasis metadata、hash、適用範囲、結果、
Claim Boundaryを正規化して提示する。

## 5. 承認粒度

承認粒度は規格名だけで固定せず、ユーザー指示、物理リスク、操作能力、計画変更可能性から
MeasurementPlanごとに決める。最低限、次の階層を提示する。

なお、本節はApprovalSession／GUI実装後の運用契約である。Season 0最初の既知IP・`*IDN?`は、
完全固定のBootstrapRunbookを人間が明示起動する実装試験として分離する。BootstrapRunbookは
MeasurementPlan承認を代替せず、物理構成、DUT、レンジ、probe設定、装置状態を変更できない。

### 承認不要の解析

ユーザーがすでに取得した保存済みartifactのReplay、描画、数理解析は、測定を新しく開始しないため
MeasurementPlan承認を要求しない。解析は原測定の不足情報を`UNKNOWN`として保持し、結果を新規の
物理観測、規格適合、正式試験へ昇格させない。

計測器上の既存bufferを読む場合は、取得開始、再arm、buffer clear、入力経路変更を伴わないことが
確認できたコマンドだけを`READ_EXISTING`とする。副作用が不明なら承認不要側へ倒さない。

ユーザーが選択した`ObservationContext`内では、オシロ画面、既存buffer、camera frame、KiCad、netlist、
設計資料をAIが繰り返し読める。読取ごとのPlan承認は要求しない。対象ID、時刻、出自、hashまたは
取得元を観測ログへ残すが、それは承認ではない。非接触可動範囲内のカメラ移動も同じ観測面に含める。
物理接触、配線移動、probe移動、信号出力を伴う可能性が出た時点で観測面から外す。

### Plan承認

AIが測定を開始する場合と入力経路を変更する場合に必須。plan hash、SourceBundle hash、instrument
capability snapshot、TTL、AbortPlan、Dev Check、Engineer Checkへ承認する。
計画の重要項目が変わった場合は承認を失効させる。

#### Reject-to-Replan loop

承認画面は各channelのrange、測定点、probe ID／倍率、coupling、impedance、GND／reference graph、DUT／source
stateを、`EngineerProbingDeclaration`と前回承認snapshotとの差分付きで提示する。ユーザーは計画が現物、意図、
許容曝露に合わない場合、`REJECTED_FOR_REPLAN`を選び、AIへ計画再作成を要求できる。

最低限のreject reason code:

- `CHANNEL_RANGE_OUT_OF_BOUNDS`
- `PROBE_ID_MISMATCH` / `PROBE_RATIO_CHANGED` / `PROBE_RATING_UNKNOWN`
- `GND_TOPOLOGY_CHANGED` / `SHARED_REFERENCE_CONFLICT`
- `COUPLING_OR_IMPEDANCE_CHANGED`
- `MEASUREMENT_POINT_CHANGED`
- `TRANSIENT_ENVELOPE_INSUFFICIENT`
- `ANOMALY_OR_ABORT_FLOW_UNACCEPTABLE`
- `ENGINEER_DECLARATION_INCOMPLETE`
- `USER_REQUIRES_REPLAN`

reject後は一切の測定開始、range変更、AUTO、source操作を許可しない。AIはreject理由、ユーザーcomment、参照evidenceを
入力として新しいplan ID／plan hashを生成し、再び承認画面へ提出する。旧計画とreject記録はappend-onlyで残し、
旧承認、TTL、Engineer Checkを新planへ暗黙継承しない。AIがreason codeを軽微として無視したり、境界値へ丸めて
承認済みに見せたりすることを禁止する。

ユーザーはapprove／rejectの最終decision authorityを持つ。これはユーザー入力だけで物理安全が証明されるという
意味ではなく、Dev Check、EngineerProbingDeclaration、機種・probe定格の必要evidenceが揃った提案について、
ユーザーが意図した測定範囲と停止方法を受諾する境界である。不足evidenceがあるplanにはapprove操作を出さない。

### Bounded Measurement Envelope

自動化された反復測定では、垂直感度やoffsetを一操作ごとに確認させず、ユーザーが事前に承認した
`MeasurementEnvelope`の内側だけをApprovalSessionへ許可する。envelopeは少なくとも次を固定する。

- DUT、測定点、channel、probe ID、probe倍率、接地点または物理GND route hash
- 期待入力電圧の通常範囲と過渡範囲、極性、周波数範囲、source impedance
- 許可する入力impedance、AC／DC／GND coupling、垂直感度、offsetの上下限
- DUT電源、保護relay、負荷、信号源等のstateと、そのstate間の許可遷移
- 規格、社内SOP、機種能力、実験目的から導出した設定変更回数、AUTO試行回数、TTL、停止条件

承認はこの不変envelopeとplan hashへ付与し、envelope内の反復だけをまとめる。電圧・周波数・probe・
coupling・impedance・物理GND・DUT／source stateのいずれかが範囲外または`UNKNOWN`なら、範囲を自動拡張
せず`HOLD_AND_REPLAN`へ移る。TTL切れ、測定点変更、物理配線変更、plan hash変更でも再承認を要求する。

自動化を開始する前に、ネゴシエーション層はADC／入力front end／probeへ実際に曝露し得る最大電圧、過渡、
offset、入力impedance、probe倍率、coupling、接地条件を`PhysicalExposureEnvelope`としてユーザーへ提示する。
最終判断はユーザーの明示承認であり、AIのrisk score、AUTO結果、過去runから暗黙承認しない。承認後は範囲内の
反復を自動化し、毎stepの確認dialogを要求しない。

一方、物理曝露を変えない探索は`ObservationWindowPolicy`へ分離し、AIが自動調整できる。

- horizontal time window、sample rate、memory depth、pre／post-trigger比
- input exposureを変えないことが確認済みのanalog bandwidth limit
- 既存artifactのFFT帯域、filter、decimation、時間区間、比較窓
- trigger条件の候補計算と、承認済み測定session内でのre-arm回数

これにより、低周波対象でも高周波漏れを確認する、音響対象でも1-bit DSD由来の帯域外noiseを探す等の
観測戦略をAIが選べる。観測窓の変更はdata-qualityと取得stateへ影響するため全変更を記録し、機種固有動作が
垂直入力経路、source出力、buffer clear、無制限re-armへ波及する場合は該当capabilityへ再分類する。

### 複数channel・複数機材・optimizer

複数channelの差分、比、位相、XY、利得、伝達特性等の数理処理と、Pairing Registryへ登録された複数機材を
使う反復評価は自動化できる。optimizerの探索空間をゼロにせず、次を`OptimizationEnvelope`として事前承認する。

- 各instrument／channelの`PhysicalExposureEnvelope`と、全channelを合わせた同時上限
- source振幅、offset、周波数、duty、負荷、DUT stateの探索範囲と刻みまたは生成規則
- channel間のGND、common-mode、差動、clock、trigger、relay、接続topology
- 利得、位相、歪み、帯域等の目的関数、制約、終了条件、最大反復または計算budget
- 機材差替え、calibration状態変化、接続喪失、時刻同期喪失時の扱い

AIはこの範囲内で探索点、観測時間、解析窓、次の候補を選べる。探索の有効性のために毎点承認を要求しない。
ただし、どれほど目的関数が改善しても、各channelまたは組合せの物理曝露範囲を越える候補は生成・送信しない。
source出力を変える探索では、計測器入力だけでなくDUT、負荷、speaker、probe、接地系の曝露も制約に含める。

測定対象が承認範囲外なら壊れ得るという工学判断はDev CheckとEngineer Checkで明示する。Engineer Checkは
実物のwork、probe、配線、GND、負荷が計画と一致することを確認し、ネゴシエーション層はその確認済み範囲を
optimizerのhard constraintとして執行する。責務を個人へ押し付ける表示ではなく、設計範囲、現物確認、
自動制約がそれぞれ何を担保したかを記録する。

#### ChannelExposureContract

`PhysicalExposureEnvelope`はinstrument全体の一つのrangeでなく、各analog channelへ
`ChannelExposureContract`を持つ。最低限、次をchannel IDと物理測定点へ固定する。

- measurement point ID、回路node、一次側／二次側、期待するreference node
- expected／maximumの`Vrms`、`Vpeak`、DC、offset、transient peakと継続時間
- probe ID、種類、倍率、最大測定電圧、最大common-mode／floating voltage、帯域
- scope BNCへ到達する換算後最大値と、機種・周波数条件付きinput rating
- AC／DC／GND coupling、input impedance、bandwidth limit、許可するV/div／offset候補
- ground leadまたは差動入力の接続先、他channelと共有するreference、絶縁境界
- load、source、relay、output transformer等、最大値算出の前提と根拠
- `display_fit`違反と`physical_exposure`違反を別reason codeで扱う閾値

V/divは表示とfront end設定の一部であり、それ単独を耐圧定格として扱わない。たとえば大振幅speaker lineへ
極端に小さいV/divを提案した場合は、画面飽和・測定不成立を`DISPLAY_RANGE_MISMATCH`として実行前に拒否する。
同時に、probe減衰後にBNCへ到達するpeak／transientとprobe／scopeの定格を独立計算し、超過または不明なら
`PHYSICAL_INPUT_LIMIT`として拒否する。表示が収まる設定でも物理定格を満たす証拠にはならない。

複数channelの契約は個別に承認するだけでなく、`SharedReferenceContract`で組合せも承認する。earth-referencedな
bench scopeではchannel referenceが共通になり得るため、異なる電位へ複数のsingle-ended ground leadを接続する
計画を、math subtractionで安全な差動測定へ変換したことにしない。高電圧またはfloating nodeは、定格と接続法を
確認した高電圧差動probe、適切な絶縁測定系等を別contractとして要求する。

このcontractの物理事実はAIが推論して埋めず、現物を扱うエンジニアの`EngineerProbingDeclaration`を正本にする。
宣言には少なくとも次の接続graphと観測根拠を含める。

- scopeの保護接地と、analog channel referenceが内部共通か独立か
- DUT chassis／signal ground／protective earth、入力信号源、dummy loadの接地関係
- isolation transformerの有無だけでなく、どの機器のどこへ入り、他の接続で再接地されていないか
- single-ended、differential、isolated probeの別、probe ID、倍率、差動定格、common-mode定格
- probe tip／reference leadの接続node、接続順序、energize前確認、取り外し順序
- USB、LAN、generator、power supply等を含む意図しないground pathの確認結果

isolation transformerがあるという一項目だけで安全を成立させない。scope、信号源、通信線、DUT chassis等から
referenceが再接続され得るため、connection graph全体を確認する。AIは宣言の欠落・矛盾・定格超過を検査できるが、
現物観測を代理したり`たぶん内部共通`を事実へ昇格させたりしない。ユーザーとエンジニアが同一人物でもよいが、
物理確認のevidenceとplan承認の意思表示は別fieldとして保存する。

すでに人間がプロービングと取得を成立させた波形を`READ_EXISTING`／`ANALYZE_STORED`で読む場合は、宣言不足を
理由に解析を拒否しない。不明な接地・probe条件を`UNKNOWN`としてprovenanceへ残す。AIがRUN、re-arm、range、
coupling、source、relay等を操作する場合だけ、有効な宣言がなければ該当write capabilityを閉じる。

承認後に人間がprobe倍率、probe ID、GND、測定点、coupling、impedanceを変更した場合は、その操作を禁止するので
なく、該当planの物理bindingを失効させる。AI起点writeを停止して新snapshotとEngineerProbingDeclarationを要求し、
Reject-to-Replan loopへ戻す。既存波形のread-only処理は継続できる。

真空管amplifierの例では、CH1／CH2のpreamp低電圧node、plate等の高電圧一次側、output transformer二次側の
4 ohm dummy loadを別のmeasurement pointとして扱う。plate電圧を二次側の最大電圧へ流用せず、二次側は
承認した出力上限、負荷値、波形crest factor、過渡条件から`Vrms／Vpeak／transient`を算出する。plateを直接
観測するchannelは、約240 Vという設計値だけで許可せず、probeのdifferential／common-mode定格、接地、過渡、
測定category、実機配線をEngineer Checkで確認する。

参考資料: SIGLENT公式
[SDS1000X-E Datasheet](https://siglentna.com/wp-content/uploads/dlm_uploads/2024/06/SDS1000X-E_DataSheet_EN04G.pdf)、
[SDS1000X-E User Manual](https://siglentna.com/wp-content/uploads/2020/04/SDS1000X-E_UserManual_UM0101E-E03C.pdf)、
Tektronix公式
[Fundamentals of Floating Measurements](https://download.tek.com/document/3AW_19134_2_MR_Letter.pdf)。

### Anomaly Contractと事前承認された退避

MeasurementPlanは自動測定開始前に`AnomalyContract`を持つ。最低限、次をplan hashへ含める。

- 異常signalの定義、対象channel、単位、閾値、持続時間、hysteresis、判定confidence
- spike、DC offset、飽和、発振、帯域外noise、GND／common-mode異常等のreason code
- どの異常でscope取得、source、DUT、relay、optimizerの何をどの順序で停止するか
- 停止時に保存するpre-trigger／post-trigger、raw buffer、設定snapshot、command log、時刻同期情報
- 部分成果物の確定、MCP handoff粒度、次のMeasurementPlanへ引き継ぐresume tokenではないevidence ID
- 定義外の逸脱、判定不能、複数異常同時発生に対するfallback

異常定義と退避flowもユーザーの明示承認対象とし、実行中にAIが危険側へ緩和しない。必要な異常分類または
fallbackが未定義なら自動測定を開始しない。異常成立後は計画に記載された停止・ログ退避・部分確定だけを行い、
新しい探索点へ進まない。次runは保存したevidenceを読めるが、旧承認を自動継承せず、新planとして承認を得る。

scope内の`GND`は二種類を分離する。計測器内部のAC／DC／GND coupling切替は列挙したenvelope内で扱えるが、
GNDからlive inputへ戻す遷移は入力曝露の再開として記録する。probeのground lead、差動probe、絶縁、
外部bypass等の物理接地変更はenvelope内の単純反復に含めず、Engineer Checkをやり直す。

### AUTO／Autosetの扱い

計測器front panelまたは独立vendor GUIで人間が直接AUTOを押す経路は、PSYCHOのAI承認経路外として
人間操作由来snapshotを取り込める。一方、AI／MCPがAUTO／Autoset commandを送る場合は、vendor機能で
あってもPSYCHOが起動した複合状態変更である。SDS1000X-Eの公式資料ではAUTOが垂直scale、水平timebase、
trigger mode等を変更するため、`READ_EXISTING`には分類しない。

初期実装では既存bufferと現在設定から候補をoffline計算する`AUTOSET_PROPOSE`を優先し、実機へ送らない。
将来`AI_REMOTE_AUTOSET`を許可するときは、次をすべて満たす。

- AUTO自体が承認envelopeに明記され、実行前snapshotとrollback候補がある
- 実行回数は規格、社内SOP、機種能力、実験目的から計画ごとに導出され、ユーザーが承認している
- AUTO結果を未承認の追加AUTO開始条件へ自動連鎖させない
- 結果を候補状態としてenvelopeと比較し、範囲外なら採用せず停止する
- `signal_presence=NOT_OBSERVED | UNKNOWN`ではrange探索を広げず、`HOLD_AND_REPLAN`へ移る
- 機種固有副作用、rollback可否、buffer clear／re-armの有無が`UNKNOWN`なら実行しない

「無信号だからさらに感度またはrangeを動かす」は許可根拠にならない。無信号、低confidence、飽和、
不安定triggerは測定対象の不在、起動前state、配線不成立、想定外DC等を区別できないためである。

参考: SIGLENT公式の
[SDS1000X-E User Manual](https://siglentna.com/download/22002/) と
[Oscilloscope Programming Guide](https://siglentna.com/download/17013/)。

### state-aware envelope: audio amplifier例

audio amplifierの起動観測では、定常波形だけを一つのrangeで扱わない。少なくとも次を別stateにする。

1. `POWER_OFF`
2. `POWER_ON_RELAY_OPEN_TRANSIENT`
3. `RELAY_CLOSE_TRANSITION`
4. `STEADY_STATE`
5. `POWER_OFF_TRANSIENT`

安全relay接続前には起動時DC spikeまたはoffsetが存在し得るため、各stateへ別の電圧・時間window、期待される
relay状態、pre-trigger条件、停止条件を与える。無信号の`POWER_OFF`またはrelay open中の観測を定常状態と
誤認してAUTOを反復しない。DUT再起動を伴う測定は、scopeのSTOP／armとDUT電源／relayのどちらを操作するかを
別stepで明記し、許可された遷移順序から外れたら停止する。

PSYCHOがrelayやDUT電源を制御しない場合も、その観測stateと人間が行う遷移をRunManifestへ残す。制御する
場合は、relay接続や再投入を単なる描画・解析操作として扱わず、固有のDev Check、Engineer Check、
ApprovalSessionを要求する。

承認済みの自動周回は、操作対象を曖昧にしない次のstate machineとして表す。

```text
ACQUISITION_STOPPED
  -> DUT_RESTART_REQUESTED
  -> SETTLING
  -> AUTOSET_BOUNDED
  -> ENVELOPE_VALIDATION
       -> CAPTURED
       -> HOLD_AND_REPLAN
       -> RANGE_EXHAUSTED

RANGE_EXHAUSTED
  -> PARTIAL_FINALIZE
  -> ARTIFACT_HANDOFF
  -> READ_ONLY_HANDOFF
```

ここで`ACQUISITION_STOPPED`はscope取得停止、`DUT_RESTART_REQUESTED`は観測対象の再起動であり、同じ
STOP／START commandとして扱わない。`SETTLING`は計画に固定した時間または観測条件で打ち切る。
`AUTOSET_BOUNDED`はenvelopeで明示承認された場合だけ存在する。試行上限はhardcodeせず、採用した規格、社内SOP、
機種能力、実験目的と停止条件から計画ごとに導出してユーザーが承認する。認可最大rangeまたは承認済み試行上限で
信号成立、飽和回避、期待DC範囲等を満たせなければ`RANGE_EXHAUSTED`とする。

`RANGE_EXHAUSTED`は測定成功へ丸めず、`INCONCLUSIVE`のreason codeとしてwarningを出す。新しい測定や
range拡張を停止し、その時点までの設定snapshot、SCPI log、取得片、timeout、判定根拠をappend-onlyで
確定する。ユーザー指定のMCP hostへ許可された粒度だけをhandoffした後は`READ_ONLY_HANDOFF`へ移り、
再承認なしに実機操作権限へ戻さない。

### Stage承認

同一の物理接続・上限・コマンド分類内で複数stepをまとめる。低リスクの反復取得等で候補になる。
承認済み`OptimizationEnvelope`内のRUN、re-arm、source設定、複数channel取得はStage承認へまとめられ、
探索点ごとのconfirmation dialogを要求しない。全stepは同じplan hash、TTL、hard constraint、AnomalyContractに
拘束される。

### Step承認

次の場合は、承認済みStage／OptimizationEnvelopeの境界を変更するため、原則としてstepごとの承認候補にする。

- プローブ位置、GND、DUT電源、回路トポロジーが変わる
- 電圧・電流、垂直感度、offset、入力インピーダンス、結合、probe倍率の上限が変わる
- AIが未承認のRUN、SINGLE、arm、再取得、source出力、trigger等で測定を開始・再開する
- 規格要求または機器能力が`UNKNOWN`
- ユーザーがstep承認を要求した

すでに承認済みStageの回数、source範囲、取得条件、停止条件に含まれるRUN、re-arm、探索stepは上記の
`未承認`に当たらず、都度承認へ戻さない。異常、範囲外、TTL切れ、物理topology変更が生じた時点でStageを
失効させる。

特にADC保護に関わる電圧上限、probe倍率、入力インピーダンス、AC/DC結合、接地は、AIの推測値だけで
実行可能状態へ移さない。機器・probeの入力定格、想定最大電圧と過渡、接続点、GND基準をユーザーが
確認できない場合は`UNKNOWN`として停止する。

時間軸変更は物理破壊方向ではなくデータ品質へ影響する操作として、上記の二者安全確認を必須にしない。
ただし変更前後、sample rate、memory depth、観測窓、既存データとの比較可能性を記録する。機種固有の
副作用として測定開始、再arm、buffer clearを伴う場合は測定開始として扱い、承認を要求する。

### 二者確認

- **Dev Check:** 開発側が設計上の期待電圧・電流、通常値、最大値、過渡、source impedance、
  許容入力範囲を確認する
- **Engineer Check:** 現場エンジニアが実際の接続点、probe倍率、接地、電圧・電流、設計超過、
  GND loop、leakage、絶縁状態を機械的に確認する

この二つは役割が違い、片方で代用しない。両方が同じDUT、測定点、物理構成、plan hashを指し、
有効期限内でなければAIは測定開始または入力経路変更を実行できない。

### hazard delta

承認判断は「係数が低いから安全」ではなく、確認済みbaselineから提案操作がどちらへ状態を動かすかで行う。

| 値 | 意味 | 扱い |
|---|---|---|
| `none` | 実機状態へ影響しない | 保存artifact解析に限定 |
| `neutral` | 入力曝露・保護・接地を悪化させないと機種契約で確認済み | 記録付きで実行候補 |
| `may_increase_exposure` | ADC、probe、DUT、接地への曝露を増やす可能性 | 二者確認とplan承認が必須 |
| `unknown` | baselineまたは副作用が未確認 | `may_increase_exposure`と同じ扱い |

低い絶対スコアでも破壊方向への差分を相殺しない。特に50 ohm入力、感度側への垂直range、probe倍率、
結合、offset、GND、測定開始は候補になる。保護方向に見える変更も、複合副作用を確認できなければ
`neutral`へ自動分類しない。

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

RUNNING
  -> RANGE_EXHAUSTED
  -> FINALIZING_PARTIAL
  -> READ_ONLY_HANDOFF

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
