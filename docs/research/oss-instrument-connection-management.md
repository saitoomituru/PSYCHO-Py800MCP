# OSS計測器接続管理メタシステム調査

状態: `[RESEARCHED]` `[Layer A]`  
調査日: 2026-07-17

## 1. 結論

PSYCHO-Py800MCPが必要とする次の全要件を一体で満たすOSSは、今回確認した範囲では見つからなかった。

- nickname、IP/hostname、任意メモをユーザーがGUI登録
- 登録時は未接続で保存できる
- 別のquery-only Link操作後にvendor/model/serial/firmware/MAC等を証拠付きで保存
- IP変更履歴、identity conflict、pairing state、capability evidenceをSQLite管理
- discovery、identity query、測定開始、設定変更の権限を分離
- AI/MCPから勝手にSCPI権限へ昇格しない

最も近いOSSは`lxi-tools/lxi-gui`である。手動追加GUIとLXI discovery backendはborrow候補になるが、
Pairing Registry正本はPSYCHO側の小さなSQLiteとして実装するのが妥当である。

## 2. 候補比較

| OSS | 使える部分 | 不足・境界 | 判断 |
|---|---|---|---|
| lxi-tools / lxi-gui | VXI-11・mDNS探索、Name/IP/protocol/port手動追加GUI、永続保存、SDS1204X-E tested | GSettings内JSON、任意メモなし、hardware evidence/historyなし、IP中心、同一GUIにSCPI実行権限 | 最有力borrow候補 |
| liblxi | VXI-11/mDNS discoveryとLXI通信のC library | registry、GUI、pairing、approvalなし | discovery backend候補 |
| ngscopeclient / libscopehal | nickname、recent connection、複数機器、YAML session、Lab Notes、offline replay、Siglent driver | 重量C++/Vulkan。Open Onlineは保存設定を実機へ再適用し得る。pairing DBではない | Season 1以降の表示・driver参照 |
| OpenTAP | Benchでinstrumentを事前構成、Resource/Connection/TestPlan分離、VISA address | .NET中心。Resource Openで試験前configureを行い得る。軽量pairing GUIではない | 責務モデルの参照 |
| QCoDeS Station | YAMLでinstrument name/address/driverを永続化、snapshot、loadまで未接続 | discovery GUI、pairing evidence、endpoint historyなし | 設定とinstance化分離の参照 |
| PyVISA / pyvisa-py | `list_resources`、VISA resource string、query/transfer backend | 永続登録、nickname、GUI、identity historyなし | Transport adapter候補 |
| sigrok / PulseView | 多数のUSB・serial・oscilloscope driver、connection string | LAN pairing registryではない。対応機種・driver差が大きい | Season 0 USB探索のborrow候補 |

## 3. lxi-tools / lxi-guiの一次コード確認

対象commit: `a66e4996f90b455ac905d12fcc8d1628e87ae6b2`（2025-05-18）

[lxi-tools README](https://github.com/lxi-tools/lxi-tools)は次を明記する。

- VXI-11またはmDNS/DNS-SDによる自動探索
- discover不能機器の手動追加
- GUI、SCPI、screenshot、benchmark、Lua automation
- tested instrumentsに`Siglent Technologies SDS1204X-E [discover+scpi+screenshot]`
- BSD-3-Clause

実装確認:

- [`lxi_gui-instrument_dialog.ui`](https://github.com/lxi-tools/lxi-tools/blob/a66e4996f90b455ac905d12fcc8d1628e87ae6b2/src/lxi_gui-instrument_dialog.ui)
  はName、IP Address、VXI11/RAW protocol、RAW port、Saveを持つ。
- [`lxi_gui-window.c`](https://github.com/lxi-tools/lxi-tools/blob/a66e4996f90b455ac905d12fcc8d1628e87ae6b2/src/lxi_gui-window.c)
  は手動登録をrandom UUID付きJSONとしてGSettingsへ保存する。
- [`io.github.lxi-tools.lxi-gui.gschema.xml`](https://github.com/lxi-tools/lxi-tools/blob/a66e4996f90b455ac905d12fcc8d1628e87ae6b2/data/io.github.lxi-tools.lxi-gui.gschema.xml)
  の`added-instruments`はstring一項目である。
- discovery結果は再検索時にlistから除去され、手動登録だけが永続化される。
- discovered deviceの重複抑止は同一IP比較である。
- 手動登録schemaは`name / id / address / protocol / port`だけで、memo、MAC、serial、firmware、
  evidence state、sighting historyを持たない。

これはユーザーが提示したGUIの前半とほぼ一致する。後半の「Link後にhardware identityを証拠付き保存」と
安全権限分離がPSYCHOの追加価値になる。

## 4. ngscopeclientの位置

[ngscopeclient](https://www.ngscopeclient.org/)はBSD-3-Clauseのcross-platform計測GUIで、nickname、
recent connection、複数機器、波形解析、Lab Notes、offline sessionを持つ。
[Getting Started](https://www.ngscopeclient.org/manual/GettingStarted.html)はsaved sessionのonline/offline
再openを区別し、[Main Window](https://www.ngscopeclient.org/manual/MainWindow.html)はYAML sessionへ
instrument/UI/waveform設定を保存する。

ただし`Open Online`はsaved channel/timebase設定を実機へ適用し得る。PSYCHOではLinkと設定変更を
分離するため、ngscopeclient sessionをPairing Registryとして直接採用しない。Season 1以降に
libscopehalのdriver分離、offline replay、waveform presentationを参照する価値がある。

## 5. OpenTAP、QCoDeS、PyVISA

- [OpenTAP Resources](https://doc.opentap.io/Developer%20Guide/Resources/Readme.html)はInstrumentをBenchで
  事前構成し、Resource Open/CloseとTestStepを分離する。ただしOpen時にconfigureする設計を許すため、
  read-only Linkとは別物である。
- [QCoDeS Station](https://microsoft.github.io/Qcodes/examples/basic_examples/Station.html)はYAMLへname、
  driver、addressを保存し、configuration loadとinstrument instance化を分離する。この遅延生成は参考になる。
- [PyVISA ResourceManager](https://www.pyvisa.org/docs/base-commands)はresource列挙とopen/queryを提供するが、
  pairing registryやGUIではない。

## 6. sigrokの位置

[sigrok supported hardware](https://sigrok.org/wiki/Supported_hardware)には多くのUSB/serial機器と一部
oscilloscopeがあり、SDS1000X系も掲載される。[Driver options](https://www.sigrok.org/wiki/Driver_options)は
複数同型機をconnection stringで区別する。SanMart等のUSB野良オシロ調査では、VID/PIDとdriver候補の
照合sourceとして有用だが、LAN Pairing Registryの代替にはならない。

## 7. 推奨borrow方針

### borrow候補

- lxi-guiの`Name + IP + protocol + port`追加・編集UX
- liblxiまたは`lxi discover`のVXI-11/mDNS discovery結果
- ngscopeclientのnickname、recent connection、offline session、driver/transport分離
- QCoDeSの「設定を読むだけでは接続しない」遅延instance化
- sigrokのUSB device/driver catalog

### borrowしないもの

- discovery直後の自動SCPI
- session open時の設定再適用
- IPをidentityとみなす重複排除
- control GUIとpairing GUIの同一権限化
- GSettings JSON一項目を監査正本にする構造

### license境界

lxi-tools、liblxi、ngscopeclient/libscopehalはBSD-3-Clause系で、Apache-2.0本体との統合候補になり得る。
ただし実際にsourceを取り込む場合は、対象commit、対象file、copyright notice、変更内容をborrow ledgerへ
記録する。CLI/subprocess利用だけの場合もversionとoutput contractを固定する。

## 8. 主張境界

本調査は公開文書と対象source commitの読解結果であり、候補OSSのinstall、build、実機接続、性能、
安全性、macOS GUI動作を検証していない。「該当OSSが存在しない」と世界全体を断定せず、今回確認した
主要候補に完全一致がなかったことだけを主張する。

### Machine-translation guardrail (en-US)

lxi-gui is the closest existing open-source reference: it already provides manual Name/IP/protocol/port
registration and VXI-11 or mDNS discovery, and lists SDS1204X-E as tested. It is not a safety-oriented pairing
registry: it stores manual entries as JSON in GSettings, lacks memo and hardware-evidence history, and exposes
SCPI control in the same application. PSYCHO should borrow discovery and UX patterns while retaining an
independent SQLite registry and authority boundary.
