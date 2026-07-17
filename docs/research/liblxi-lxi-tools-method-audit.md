# liblxi / lxi-tools Method & Integration Audit

状態: `[RESEARCHED]` `[Layer A]`
調査日: 2026-07-17

## 1. 結論

最初のnative middlewareは、`liblxi`の小さな公開C APIを使うPSYCHO専用observer sidecarがよい。
`lxi-tools`全体をlibraryとしてincludeする構成は採らない。

- `liblxi`はtransport SDKとして利用候補にする
- `lxi-tools`はCLIをPSYCHOの常設APIにせず、機種判別・screenshot command・実装上の例外を抽出する
  upstream referenceとして扱う
- PythonとはC ABIで直接密結合せず、native sidecarとversion付きJSON Linesで接続する
- Phase 0のsidecarは`discover / identify`だけをcompile-time allowlistする
- screenshot pluginはcommandごとに副作用を再分類する。upstreamの`screenshot`という名前だけで
  `READ_EXISTING`へ分類しない
- runtime時にInternetから最新版を取得しない。build時にcommit/version/hashを固定し、配布時はOS・architecture別の
  検証済みbinaryを同梱または明示installする

`SDKを横に置いて動的に引っ張る`構成はmacOSでは成立し得る。ただしPythonが直接`dlopen`するより、
PSYCHO native observerが`liblxi.dylib`へdynamic linkし、Pythonはsidecarだけを起動する方がfailure isolationと
権限境界を保ちやすい。WindowsはupstreamがCygwin/WSL2を主な経路としており、native MSVC DLLを同じ前提で
扱えるとはまだ確認できていない。

## 2. 調査対象と除外範囲

### 対象

- `liblxi` 1.22
  - commit: `b14716ba12f296cb0d35640df5dcb84889fd978d`
  - commit date: 2025-04-03
- `lxi-tools` source
  - commit: `a66e4996f90b455ac905d12fcc8d1628e87ae6b2`
  - commit date: 2025-05-18
- Homebrew formula metadata
  - `liblxi` 1.22
  - `lxi-tools` 2.8
- 調査host
  - macOS 15.7.7
  - `x86_64` Hackintosh

### 除外

- package install
- source build
- symbol load test
- Apple Silicon実機build
- Windows実機build
- 計測器への接続、VXI-11、mDNS、SCPI送信
- SDS1204X-Eの`screenshot`副作用実機確認

## 3. liblxi公開API

公開headerの操作面は7関数である。

| API | 役割 | PSYCHOでの候補 | 注意点 |
|---|---|---|---|
| `lxi_init()` | 1024件のstatic session tableを初期化 | sidecar起動時に一回 | active session中の再初期化を許可しない |
| `lxi_discover()` | VXI-11またはmDNS探索 | bounded discovery backend候補 | blocking callback型。探索方式を明示する |
| `lxi_discover_if()` | 指定interfaceで探索 | VXI-11限定候補 | `ifname`はmDNSでは明示的に無視される |
| `lxi_connect()` | VXI-11/RAW sessionを開く | Link/identify時のみ | HiSLIP enumはあるが接続実装はない |
| `lxi_send()` | 任意byte列を送信 | observer内の固定commandだけ | SCPI安全分類、改行付与を行わない |
| `lxi_receive()` | caller bufferへbyte列を受信 | ID/画像/binary取得候補 | NUL終端しない。byte countを正本にする |
| `lxi_disconnect()` | session切断 | finally相当で必須 | timeout/error時の結果も記録する |

公開型:

- `lxi_info_t`: `broadcast / device / service` callback
- protocol: `VXI11 / RAW / HISLIP`
- discovery: `DISCOVER_VXI11 / DISCOVER_MDNS`
- success/error: `LXI_OK=0 / LXI_ERROR=-1`

### 3.1 APIにないもの

- structured error code/detail
- runtime library version getter
- capability model
- SCPI command classification
- response framing abstraction
- reconnect policy
- authentication/TLS
- pairing registry
- cancellation token
- per-session concurrency contract
- instrument vendor/model parser

errorは主に`-1`とstderrで返る。PSYCHO sidecarはoperation、timeout、phase、transport、stderr summaryを
独自error envelopeへ正規化する必要がある。

### 3.2 transport実装上の観測

- VXI-11はRPCと`inst0`を使用する。Darwin以外では`libtirpc`依存が必要になる構成である
- RAWはIPv4 TCP socketで、port、改行、message framingをcallerが管理する
- mDNS backendはAvahi、Bonjour、Cygwin DNS-SDからbuild時に選ばれる
- mDNS backendが一つもbuildされなかった場合、`mdns_discover()`は結果なしでreturn 0する
- `lxi_discover_if()`のinterface指定はVXI-11だけに適用され、mDNSでは無視される
- service catalogにHiSLIPがある一方、`lxi_connect(..., HISLIP)`はerrorになる
- libraryはshared libraryとしてbuildされ、headerとpkg-config metadataをinstallする

このため、`APIが成功を返した`と`有効なbackendで観測した`を同一視しない。build capabilityを別manifestへ
記録する。

## 4. lxi-toolsの機能層

`lxi-tools`は再利用用shared libraryではない。共通C sourceをCLI `lxi`とGTK GUIへそれぞれcompileしている。

### 4.1 CLI command

| command | 内容 | PSYCHO判断 |
|---|---|---|
| `discover` | VXI-11またはmDNS探索 | 調査・比較用。stdout parseを恒久APIにしない |
| `scpi` | 任意SCPI、interactive、RAW、hex | AIへ直接公開しない |
| `screenshot` | ID自動判別＋機種別取得 | profile抽出元。command単位で副作用監査 |
| `benchmark` | `*IDN?`を既定100回反復 | Phase 0では使用しない |
| `run` | Lua automation | Approval実装前はincludeしない |

CLI出力は人間向けtextで、stable JSON contractではない。subprocess adapterは最初の比較試験には使えるが、
Pairing RegistryやMCPの正本APIにはしない。

### 4.2 Lua layer

Luaへ次を公開する。

- `lxi_connect / lxi_disconnect`
- `lxi_scpi / lxi_scpi_raw`
- `lxi_sleep / lxi_msleep`
- clock create/read/reset/free
- in-memory logとCSV保存helper

これは有用なautomation実装例だが、任意SCPIとfile writeを持つ。Phase 0 observerへ含めない。

### 4.3 GUI layer

- discovery
- 手動Name/IP/protocol/port登録
- GSettings内JSON保存
- SCPI terminal
- screenshot/live view
- benchmark
- Lua editor/runner
- 簡易chart/CSV/PNG

GUIのUXは参照できるが、発見・台帳・任意SCPI・automationが同じauthorityに存在する。PSYCHOではそのまま
移植しない。

## 5. screenshot plugin監査

確認したcommitでは24個のpluginがcompile-time登録される。pluginは次の3要素を持つ。

- plugin name
- description
- `*IDN?`応答へ照合するregex群
- screenshot関数pointer

Siglent SDS 1000X/2000X系はVXI-11接続後に`scdp`を送信し、最大4 MiBを受信してBMPとして保存する。
これはSDS1204X-Eの最初のprofile候補になる。

ただしplugin群全体はquery-onlyではない。確認した例には次がある。

- instrument内へ一時画像fileを生成する
- screenshot format、compression、layout、port、theme等を変更する
- instrument内の一時fileを削除する
- 変更前設定をqueryし、後で復元する
- `*WAI`やoperation complete待ちを行う

したがって`screenshot`を一つの共通capabilityにせず、最低限次へ分ける。

```text
SCREEN_READ_DIRECT
SCREEN_CAPTURE_TRIGGER
DISPLAY_SETTING_CHANGE
INSTRUMENT_FILE_CREATE
INSTRUMENT_FILE_READ
INSTRUMENT_FILE_DELETE
SETTING_RESTORE
```

SDSの`scdp`も、名称やupstream実績だけで`READ_EXISTING`へ確定しない。画面capture生成、acquisition re-arm、
buffer clear、設定変更の有無をSDS1204X-E実機とfirmware条件で観測してから分類する。

## 6. include方式比較

| 方式 | 軽さ | crash隔離 | 再現性 | 権限境界 | 判断 |
|---|---:|---:|---:|---:|---|
| Python `ctypes/cffi`で`liblxi`を直接load | 高 | 低 | 中 | 中 | API taste test候補。常設MCPには非推奨 |
| PSYCHO C sidecarをdynamic link | 高 | 高 | 高 | 高 | 第一候補 |
| `lxi` CLIをsubprocess実行 | 中 | 高 | 中 | 低 | upstream比較試験だけ |
| liblxi sourceをsubproject build | 中 | 高 | 最高 | 高 | 配布段階のfallback |
| lxi-tools共通sourceを丸ごとinclude | 低 | 中 | 中 | 低 | 採らない |

### 6.1 推奨runtime layout

```text
runtime/native/
  macos-x86_64/
    psycho-lxi-observer
    liblxi.1.dylib
    runtime-manifest.json
    LICENSES/
  macos-arm64/
    psycho-lxi-observer
    liblxi.1.dylib
    runtime-manifest.json
    LICENSES/
  windows-x86_64/
    UNKNOWN until native backend is selected
```

macOS sidecarは`@loader_path`相対で同梱dylibを解決できる構成を候補にする。system/Homebrew版を使うdeveloper
modeと、検証済みdylibを同梱するrelease modeを混同しない。

### 6.2 runtime downloadを既定にしない

起動時にGitHub/Homebrewから最新版を取得すると、offline-first、provenance、再現性、supply-chain、
architecture一致が崩れる。取得が必要ならinstaller/update operationとして分離し、次を確認してから配置する。

- platform / architecture
- upstream version / commit
- artifact hash
- license bundle
- code signatureまたは配布元検証
- PSYCHO側adapter compatibility

## 7. platform判断

### macOS x86_64

今回のhost。Homebrew formulaは`liblxi 1.22`を提供し、macOS systemのlibxml2等を利用する。未install・未build
なので動作はまだ`UNKNOWN`である。

### macOS arm64

sourceはDarwin/Bonjour分岐を持つが、今回Apple Siliconでbuildしていない。x86_64 dylibをarm64 processへload
できないため、native arm64 artifactを別に作り、同じmethod contractを試験する。

### Windows x86_64

upstream文書はWindows installerをexperimentalとし、sourceにはCygwin DNS-SD分岐がある。WSL2経路も案内する。
これはnative MSVC DLLの安定提供を意味しない。Cygwin runtimeを同梱する案、WSL2 sidecar、別VXI-11 backendを
比較するまで`UNKNOWN`とする。

## 8. Phase 0 native observer contract

最初にincludeするmethodは絞る。

```text
INITIALIZE
DISCOVER_VXI11_BOUNDED
DISCOVER_MDNS_BOUNDED
IDENTIFY_IDN_QUERY
DISCONNECT
```

含めないmethod:

```text
RAW_SCPI_ARBITRARY
INTERACTIVE_SCPI
BENCHMARK_LOOP
LUA_RUN
SCREENSHOT
RUN_OR_ARM
RANGE_OR_INPUT_CHANGE
```

Pythonへ返す値はnative pointerやsession handleではなく、schema version付きresultとartifact referenceに限定する。
session handleはsidecar process外へ出さない。

## 9. 次の検証単位

1. `liblxi 1.22`を現在のx86_64 Macへdeveloper dependencyとして導入する計画を作る
2. 実機I/Oなしでshared library path、architecture、required symbol 7件、link dependencyを検査する
3. native observerのJSON request/response schemaとallowlist testを先に作る
4. `discover`だけをupstream CLIとPSYCHO sidecarで比較するrunbookを作る
5. 別承認後に`*IDN?`一回だけのLink実験を行う
6. screenshotはその後、`scdp`の副作用仮説と中止条件を持つ別runbookにする

## 10. License / provenance

`lxi-tools`はBSD-3-Clause。`liblxi`はBSD-3-Clauseを基本とし、VXI-11由来fileにはEPICS license条件がある。
sourceまたはbinaryを配布する場合は対象version、copyright、license text、変更有無を
`THIRD_PARTY_NOTICES`とborrow ledgerへ残す。

## 11. Claim Boundary

これは公開sourceとHomebrew metadataの静的調査結果である。build、load、実機接続、timeout挙動、ABI互換、
Apple Silicon、Windows native動作は検証していない。source上にmethodやplatform分岐が存在することを、対象環境で
動作した事実へ昇格させない。

### Machine-translation guardrail (en-US)

liblxi exposes a small seven-function C API and is a reasonable transport SDK candidate. lxi-tools is an
application, not a stable middleware library; its CLI, Lua automation, GTK GUI, and 24 screenshot plugins are
compiled from shared source files. Several screenshot plugins change instrument settings or create and delete
files, so the upstream `screenshot` label must not be treated as a read-only safety classification. PSYCHO should
use a narrow native observer sidecar, pin and verify the runtime binary, and expose only versioned JSON results to
Python. Native Windows support and Apple Silicon builds remain unverified.
