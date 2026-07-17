# Authority Proportionality & Local Bench Trust

状態: `[DESIGNED]` `[Layer A]`

## 1. 目的

安全機構を「AIが関与したので全部承認」「計測器なので全部秘密」といった一律制限へ倒さず、実際の
物理副作用、操作起点、network境界に比例させる。過剰な承認と過剰な秘匿は、現場が安全機構を迂回する
圧力を生み、証拠を欠落させるため、それ自体が安全上のfailure modeになり得る。

## 2. 操作起点を分ける

### 2.1 人間が独立GUIを直接操作

lxi-gui、ngscopeclient、vendor GUI、計測器front panelを人間が直接操作する経路へ、PSYCHOの
AI ApprovalSessionを横から強制しない。PSYCHOはその外部GUIの安全性を保証せず、必要なら人間操作として
時刻、artifact、設定snapshotを受け取る。

人間GUIが常に安全だという主張ではない。物理操作の判断主体と実行主体が人間であり、AIが自動開始する
経路とはガバナンス対象が違う、という境界である。

### 2.2 AIが物理状態変更を起動

AI/MCPが次を起動する場合はMeasurementPlan、Dev Check、Engineer Check、ApprovalSessionを要求する。

- RUN、SINGLE、arm、re-arm、trigger開始
- vertical range、offset、probe倍率、coupling、input impedance
- probe位置、GND、DUT接続、信号源、電源状態
- 機種契約上、副作用が不明な操作

### 2.3 成立済み観測をAIが読む

人間がprobe、trigger、RUNを成立させ、すでに画面またはbufferへ存在する波形を読む、保存する、解析する
行為には、測定開始承認を要求しない。

- screen、測定値、既存bufferのquery-only read
- ユーザーがexportしたCSV/binary/image
- 保存artifactのReplay、描画、FFT、統計、比較
- 既存波形から必要区間だけを切り出す

機種固有commandがbuffer生成、re-arm、clear、設定変更を伴う場合だけ、実際の副作用へ再分類する。

## 3. authority matrix

| 起点 | 操作 | PSYCHOのAI承認 | 記録 |
|---|---|---|---|
| 人間 / 独立GUI | 人間が直接RUN・range変更 | 強制しない | import可能なsnapshot/artifactだけ記録 |
| AI | 保存済みartifact解析 | 不要 | artifact provenance |
| AI | 成立済み画面・bufferのquery-only read | 不要 | ObservationContextとread log |
| AI | data-qualityだけの既知timebase変更 | safety承認不要 | 前後設定とdata影響 |
| AI | RUN・arm・re-arm | 必要 | plan/check/approval/command/result |
| AI | vertical/input path変更 | 必要 | plan/check/approval/command/result |
| AI | AUTO／Autoset | 承認envelope内だけ許可 | 前後snapshot、候補採否、停止理由 |
| AI | 副作用不明 | 必要側へ倒す | unknown reasonと解消手順 |

### 3.1 不可逆性でgateを分ける

PSYCHOが最も強く閉じる対象は、AI起点の操作またはプロービング指示がADC／入力front end、probe、DUT、
信号源、接地系を破損させ、再構成不能な物理状態へ遷移させる経路である。`V/div`だけでなく、offset、
50 ohm／1 Mohm入力、coupling、probe倍率、接地点、source出力、DUT電源、GND loopを一つの
`PHYSICAL_EXPOSURE_CHANGE`群として扱う。

表示rangeを安全側へ見せることは、probe先の電圧、probe rating、接地、入力端の実際の曝露を安全にした証拠に
ならない。機種別commandの前に、物理sourceと入力経路の両方をDev Check／Engineer Checkで確認する。

| class | 例 | PSYCHO既定control |
|---|---|---|
| `IRREVERSIBLE_PHYSICAL` | probe/GND指示、input impedance、range、offset、source、電源 | plan＋Dev Check＋Engineer Check＋ApprovalSession |
| `MEASUREMENT_EXECUTION` | AIによるRUN、SINGLE、arm、再取得 | plan＋checks。機種契約確定後に条件付き細分化可 |
| `REVERSIBLE_INSTRUMENT_STATE` | GUI表示、保存形式、非物理的な表示設定 | before/after snapshot、command log、restore結果 |
| `INSTRUMENT_STORAGE_MUTATION` | 機器内file作成・上書き・削除 | 対象path、目的、結果、rollback／cleanup log |
| `DATA_EGRESS` | MCP hostへartifactまたはsliceを返す | 宛先と範囲を表示。外部host契約へ責務handoff |
| `READ_OR_ANALYZE` | 既存波形、保存artifact、FFT、描画 | 物理承認不要。provenanceを記録 |

復元可能な設定変更や機器内file操作を、ADC損傷と同じ二者物理承認へ一律に持ち上げない。代わりに
transaction log、baseline snapshot、restore／cleanup結果を残す。逆にlogがあることは、不可逆な物理操作を
許可する根拠にはならない。

### 3.2 外部AI hostとのデータ契約

ユーザーが選択したMCP／AI hostの保存、学習利用、再配布、retention policyをPSYCHOが代行審査・保証しない。
PSYCHOが担当するのは、自身が実装するegressについて次を明示し、依頼範囲外へ自動送信しないことである。

- 何を返すか: summary、slice、画像、artifact全体
- どのhost／sessionへ返すか
- localに残る原本と、境界外へ出る派生物
- PSYCHOによるtelemetry／cloud uploadの有無

明示されたegress後の利用条件はユーザーと接続先providerの契約境界へhandoffする。外部providerのpolicyを
理由に、localのread、解析、証拠保存を一括停止しない。一方、PSYCHO自身が表示した範囲を越えて送信した場合は
PSYCHO側の実装不具合であり、`外部vendorの問題`として転嫁しない。

### 3.3 AI接続を技能代替にしない

AI接続は、物理作業の経験、現物確認、probe／接地技能、作業者本人の受諾を代替しない。組織上のmanager、
budget owner、AI providerが`AIがあるので実行可能`と判断しただけではEngineer Checkを成立させない。

`IRREVERSIBLE_PHYSICAL`または`MEASUREMENT_EXECUTION`の実行前に、少なくとも次をplan hashへ結び付ける。

- 実際にprobe、配線、接地、電源を扱うexecutor
- executor本人による対象stepと停止条件の確認・明示受諾
- Dev Checkを行った主体と設計根拠
- Engineer Checkを行った主体と現物観測
- 不足する技能、人員、probe、絶縁、保護具、時間

AIの自己申告、managerによる代理入力、`ソフトウェア担当者の手が空いている`というresource判断だけでは
physical readinessをtrueにしない。不足時は危険操作だけをblockし、既存波形のread、解析、計画修正、
必要人員・機材の提示は継続する。表示は個人へ責任を押し付けるのでなく、計画と資源の不足を示す。

### 3.4 承認は操作列でなく物理envelopeへ付与する

反復取得や自動化では、承認済みのDUT、測定点、probe、物理GND、入力impedance、coupling、期待電圧・
過渡・周波数、DUT／source state、設定変更回数、TTLを`MeasurementEnvelope`として固定する。
envelope内の設定stepへ都度承認を要求しない一方、範囲をAIが自己拡張することも許可しない。

ADC／入力front endへ関わる`PhysicalExposureEnvelope`は自動化前にユーザーが最終承認する。これとは別の
`ObservationWindowPolicy`では、物理曝露を変えない時間窓、sample rate、memory depth、pre-trigger、
bandwidth limit、派生解析帯域をAIが選べる。高周波対象の低周波漏れ、音響対象のDSD帯域外noise等を
探索するたびに再承認を要求せず、変更とdata-quality影響だけを証拠へ残す。

特に`signal_presence=NOT_OBSERVED | UNKNOWN`は安全側の低スコアではなく、入力条件を判断できない独立gateで
ある。AUTO／Autosetを繰り返して垂直rangeを探索せず、現在の承認状態を保持して計画修正へ戻る。
人間がfront panel等で直接AUTOを使う経路と、AIがAUTO commandを送る経路を区別する。後者は垂直軸、
時間軸、triggerをまとめて変え得るため、複合状態変更としてenvelope、試行上限、前後snapshotを要求する。

起動過渡のあるDUTは状態別envelopeを持つ。たとえばaudio amplifierでは、relay開放中の起動DC spike、
relay接続遷移、定常状態、停止過渡を分離する。無信号の起動前stateを定常状態と誤認してrangeを追従させない。

## 4. Local Bench Trust Profile

### 4.1 `LOCAL_BENCH`

初期default。NATを跨がない管理下LAN、local host、直接接続USBを想定する。

- private/local IP、nickname、vendor、model、firmware、通常動作logはcredentialではない
- serialとMACもlocal operational metadataとしてSQLiteへ保存可能
- SQLiteはOS account permission、transaction、backup、integrity checkを基本controlとする
- database全体の高度暗号化を必須にしない
- 生DBをMCP response、公開Git、telemetryへ自動添付しない

### 4.2 `AUTHENTICATED_LAN`

機器password、API key、client certificate等が存在する場合、credentialだけをOS keychain等のsecret storeへ
分離する。Pairing Registryにはsecret本体でなくreferenceを置く。

### 4.3 `ROUTED_OR_WAN`

router越し、VPN越し、Global IP、第三者networkへ出る場合は明示opt-in、endpoint allowlist、認証、暗号化、
timeout、監査scopeを別途要求する。`LOCAL_BENCH`の推定を継承しない。

## 5. 内部保存と公開exportは別問題

内部SQLiteへ保存できることと、公開repositoryへ掲載できることを混同しない。

- local runtime: 再現性と機械迷子防止を優先し、local IPとhardware identityを保持
- project-private backup: ユーザー指定の保全方針に従う
- public documentation: ユーザーが選んだlocal segment情報だけを掲載し、credential、未匿名化serial、
  MAC、生DBは既定で除外

公開制限を理由に、local evidence自体を採取しない設計へ倒さない。

## 6. Anti-SaaS Responsibility Evasion

安全gateを、サービス提供者が責任を避けるための包括拒否へ変形させない。

禁止する挙動:

- `AI操作だから`という理由だけでread-only解析まで拒否する
- すでにユーザーが取得した波形を、過去の計画承認がないため読めなくする
- local IPや機種logをcredentialと同格に扱い、再現記録を消す
- 規格、契約、物理hazardを特定せず、一般的な免責文だけで停止する
- 承認済み条件を毎readで再承認させるconfirmation loop
- safety disclaimerを実際のinterlock、stop condition、evidenceの代用品にする
- 危険を理由にBenefitと目的を表示から消し、`やらない`だけを安全策にする

拒否またはblockを返す場合、最低限次を返す。

```json
{
  "blocked_capability": "INPUT_PATH_CHANGE",
  "specific_hazard": "probe attenuation is unverified",
  "missing_evidence": ["Engineer Check: probe ratio"],
  "how_to_proceed": ["record probe ratio", "rebuild plan snapshot"],
  "allowed_now": ["READ_EXISTING", "ANALYZE_STORED"]
}
```

blockは全機能停止でなく、危険なcapabilityだけを閉じる。安全に続行できる観測、保存、解析、部分成果物の
確定は残す。

## 7. 受入条件

- 保存artifact解析がApprovalSessionなしで動く
- `READ_EXISTING`を反復しても都度承認を要求しない
- AIによるRUNとvertical変更は承認なしに実行できない
- 独立した人間GUIへPSYCHOのAI承認を注入しない
- local IP、model、firmwareをSQLiteへ通常保存できる
- credentialが追加された時だけsecret store referenceを要求する
- block responseが具体的hazard、missing evidence、解消手順、継続可能capabilityを返す
- presentation scoreや免責文がengineering gateを代替しない
- 復元可能な設定・機器内file操作を不可逆な物理損傷と同じgateへ一律分類しない
- 外部AI hostのpolicyを理由にlocal read／解析を停止せず、egress範囲と責務handoffを表示する
- AI、manager、budget ownerの代理入力だけでEngineer Checkまたはexecutor受諾を成立させない
- 無信号またはsignal不明を理由にAUTO／range探索が承認envelopeを拡大しない
- 起動過渡、relay遷移、定常状態を同じ入力条件として扱わない
- 最終的な物理曝露rangeをユーザーへ提示して承認し、観測窓のAI裁量と混同しない

### Machine-translation guardrail (en-US)

Approval follows physical side effects and action origin, not the mere presence of AI or an instrument.
Reading and analyzing an already-established waveform does not require measurement-start approval. Direct
human operation in an independent GUI is outside PSYCHO's AI approval path. Local bench IP addresses and
ordinary instrument logs are operational metadata, not credentials by default. Safety gates must identify a
specific hazard, preserve safe read-only work, and provide a concrete path forward rather than a blanket
liability-avoidance refusal. PSYCHO does not treat external AI-provider data policy as a physical-safety gate,
but it must disclose and honor the egress boundary it implements. Connecting AI does not substitute for the
physical skills, on-bench checks, and explicit acceptance of the person performing the work.
Approval may cover a bounded, immutable measurement envelope rather than every individual command. No-signal
or unknown-signal states never authorize automatic range expansion. AI-triggered autoset is a composite
state change, while autoset used directly by a human on the instrument remains outside PSYCHO's AI path.
