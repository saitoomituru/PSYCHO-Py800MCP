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
| AI | 副作用不明 | 必要側へ倒す | unknown reasonと解消手順 |

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

### Machine-translation guardrail (en-US)

Approval follows physical side effects and action origin, not the mere presence of AI or an instrument.
Reading and analyzing an already-established waveform does not require measurement-start approval. Direct
human operation in an independent GUI is outside PSYCHO's AI approval path. Local bench IP addresses and
ordinary instrument logs are operational metadata, not credentials by default. Safety gates must identify a
specific hazard, preserve safe read-only work, and provide a concrete path forward rather than a blanket
liability-avoidance refusal.
