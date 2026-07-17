# Instrument Discovery & Pairing Registry

状態: `[DESIGNED]` `[NOT_OBSERVED: instrument mDNS service, run 20260717-mdns-ssdp-01]`

## 1. 目的

LAN計測器のIPがDHCP等で変わっても機器を迷子にせず、発見したnetwork endpointと、人間が確認済みの
計測器identityを分離して管理する。探索は低侵襲な方式から段階的に行い、発見だけでSCPI権限や
ペアリングを生成しない。

## 2. 現時点の根拠

- `[FACT: vendor documentation]` SDS1000X-E系はVXI-11、Web control、SCPI Socket 5025、
  SCPI Telnet 5024を公式資料で掲げている。
- `[FACT: vendor documentation search]` 確認したSDS1000X-E User ManualとProgramming Guideには、
  mDNS、Bonjour、DNS-SD、mDNS hostnameの明記を確認できなかった。
- `[FACT: LXI specification]` LXI 1.3以降のconformant deviceはmDNS/DNS-SDをsupportする。
- `[UNKNOWN]` SDS1204X-Eの現在firmwareがmDNS/DNS-SD広告を実際に出すか、どのservice typeを広告するか。
- `[INFERRED]` SIGLENT資料の「VXI-11 (LXI)」表記だけでは、LXI適合versionやmDNS実装を断定できない。

参照:

- [SIGLENT SDS1000X-E Programming Guide](https://www.siglent.com/wp-content/uploads/2024/08/SDS1000-SeriesSDS2000XSDS2000X-E_ProgrammingGuide_PG01-E02D-1.pdf)
- [SIGLENT SDS1000X-E Datasheet](https://int.siglent.com/u_file/download/24_07_01/SDS1000X-E_DataSheet_EN04G.pdf)
- [LXI Device Specification 1.6.1](https://public.lxistandard.org/specifications/LXI_1.6_Specifications/LXI_Device_Specification_1.6.1_2024-01-18.pdf)

## 3. 用語境界

BonjourはAppleのmDNS/DNS-SD実装・製品名であり、mDNSと競合する別の探索規格として扱わない。
実装契約では`mdns_dns_sd`、macOS上のprovider表示では`Bonjour`を使用する。

次を分離する。

- **discovered endpoint:** network上に何かが広告または応答した
- **identified instrument:** query-only識別でvendor/model等を観測した
- **paired instrument:** 観測identityを人間が対象機として確認した
- **capable instrument:** 個別capabilityを実験で確認した

`discovered != identified != paired != capable`とする。

## 4. 探索順序

ローカルregistryはnetwork I/O前に読み、既知identityと過去endpointを候補照合へ使う。network探索は
次の順序で段階的に許可する。

1. `mDNS/DNS-SD browse`
   - `_lxi._tcp.local.`
   - `_vxi-11._tcp.local.`
   - `_scpi-raw._tcp.local.`
   - `_scpi-telnet._tcp.local.`
   - `_http._tcp.local.`は候補補助に限定し、一般Web機器を計測器認定しない
2. `user-supplied exact IP`
   - mDNS広告が観測されない場合、ユーザーが画面で確認した完全一致IPだけを候補化する
3. `VXI-11 discovery`
   - 明示したinterfaceとsubnetに限定したUDP/RPC portmapper discovery
4. `bounded subnet probe`
   - 対象CIDR、port、packet、回数、timeoutを固定した最後の手段

mDNS browseもnetwork packetを送受信する実験である。offline処理として偽装せず、runbook hashと人間の
明示起動を要求する。ただしSCPI送信、設定変更、取得開始とは別capabilityにする。

## 5. mDNS観測runbook要件

- 使用network interfaceを一つに固定
- 対象service typeを上記allowlistへ固定
- 観測時間を有界化し、自動常駐させない
- browse queryと受信recordを原本保存
- service instance、hostname、SRV port、TXT、A/AAAA、TTL、interface、timestampを記録
- 観測なしを`NOT_OBSERVED`とし、非対応断定へ変換しない
- 広告されたhostname、TXT、portを未信頼入力として長さ・文字種・件数制限する
- mDNS結果から自動的にWeb page、VXI-11、SCPI Socketへ接続しない

最初の試験は「広告を観測できたか」だけを判定し、機器識別は別のquery-only runbookへ渡す。

## 6. SQLite Pairing Registry

推奨local pathはGit外の`state/private/instrument-pairing.sqlite3`とする。生DB、IP、MAC、未匿名化serialを
Gitへcommitしない。schema migration versionと生成アプリversionを保持する。

### 6.1 tables

#### `instruments`

- `instrument_id`: project内UUID。IPやhostnameをIDにしない
- `nickname`: ユーザーが付けるproject-local表示名。rename履歴を残す
- `user_memo`: 任意メモ。実行可能contentとして扱わない
- `vendor`, `model`, `serial_private`, `firmware_last_seen`
- `pairing_state`: `discovered / identified / user_paired / conflict / revoked`
- `first_seen_at`, `last_seen_at`, `paired_at`
- `user_confirmation_ref`

#### `endpoints`

- `endpoint_id`, `instrument_id`
- `transport`: `mdns / vxi11 / scpi_raw / scpi_telnet / http`
- `hostname`, `ip_address`, `port`, `network_interface`, `subnet_scope`
- `first_seen_at`, `last_seen_at`, `record_ttl`, `source_sighting_id`
- `active_state`: `candidate / verified / stale / conflict`

endpointは履歴として残し、IP変更時に上書き消去しない。

#### `sightings`

- 観測run、時刻、method、raw artifact ID、広告service/TXT、応答分類
- `observed / not_observed / malformed / timeout / conflict`
- evidence hash

#### `identity_evidence`

- source: `idn_response / mdns_txt / user_entry / mac_observation / vendor_web`
- observed valueまたはprivate valueへのreference
- confidenceではなく`evidence_state`
- timestamp、artifact ID
- MAC addressは取得できた場合だけ`mac_observation`として保存し、恒久identityや必須fieldにしない

#### `capabilities`

- capability name、`designed / detected / identified / data_verified / control_verified`
- firmware、transport、evidence artifact、last verified

## 7. identity照合とpairing

mDNS instance名、hostname、IP、MACのいずれか一つを恒久identityにしない。DHCP、hostname conflict、
network adapter変更、firmware差で変化し得るため、identity evidence setとして扱う。

pairing昇格には最低限、次を必要とする。

1. discovery sighting
2. 別runbookによるquery-only identity応答
3. vendor/model/serial/firmware等、実際に返ったfieldの原本保存
4. ユーザーによる対象機確認
5. endpointとidentityの結合event保存

同一endpointから前回と異なるidentityが返る、または同一identityが同時に複数endpointへ現れた場合は
`conflict`へ倒し、自動再pairしない。serialが空または重複する機種も想定し、単一field一致で昇格させない。

### 7.1 新規追加GUI

ユーザー導線を二段階に分ける。

#### `保存（未接続）`

- 必須: nickname、IPまたはhostname
- 任意: memo、transport候補、port
- 保存結果: `DRAFT`
- network I/O: なし
- hardware field: 未観測なので`UNKNOWN`

#### `Linkして本人確認`

- 別のquery-only runbookと明示起動を要求
- 成功時に実際の応答からvendor、model、serial、firmware、transport endpointを保存
- local neighbor tableで取得できた場合だけMAC observationを保存
- MACが取得不能でも失敗にしない。router越しでは対象MACを得られず、adapter交換等で変わり得る
- user入力値とobserved値を同じcolumnへ混ぜず、sourceとtimestampを保持
- 最終的な`USER_PAIRED`昇格は観測結果をGUIへ返し、ユーザー確認後に行う

`保存`buttonからLinkやSCPIを暗黙実行しない。`Link`は測定開始、buffer取得、設定変更を許可しない。

### 7.2 GUI状態

```text
DRAFT
  -> LINK_REQUESTED
  -> IDENTIFIED
  -> USER_PAIRED
  -> STALE / CONFLICT / REVOKED
```

nicknameは人間可読aliasであり、identity証拠ではない。IP変更時はendpoint eventを追加し、nicknameと
instrument IDを維持する。

### 7.3 OSS borrow判断

`lxi-tools/lxi-gui`はName、IP、VXI11/RAW protocol、portの手動追加GUI、GSettings永続化、VXI-11/mDNS
探索を持ち、tested listにSDS1204X-Eを含む。GUI導線とliblxi discoveryはborrow候補とする。

ただし同OSSは任意memo、SQLite、hardware evidence history、pairing state、approval分離を持たず、同じGUIに
SCPI/screenshot/script権限があるため、そのままPairing Registry正本にしない。調査詳細は
[`../research/oss-instrument-connection-management.md`](../research/oss-instrument-connection-management.md)を参照する。

## 8. 起動時の再発見

1. registryをread-onlyで開き、paired identityとendpoint履歴を読む
2. mDNS/DNS-SDを有界browseし、stable identity候補へ照合する
3. 一致候補がなければlast-known endpointを`stale candidate`として提示する
4. ユーザー指定IPがあれば候補へ追加する
5. query-only gate内でidentityを再確認する
6. 一致後だけ`verified endpoint`へ更新する

last-known IPへ黙ってSCPI送信しない。別機器へDHCP leaseが移った可能性を常に考慮する。

## 9. 保全と公開境界

- SQLiteはWAL modeとtransactionを使い、pairing eventをatomicに保存する
- migration前に整合検査とrecoverable backupを作る
- DB破損時はnetwork探索から再構成できるよう、raw sighting artifactを別保存する
- 公開ログにはIP、MAC、serial、生SQLiteを出さない
- 必要ならvendor/model、内部instrument ID、redacted endpoint countだけを公開manifestへexportする
- credential、ApprovalSession token、SCPI秘密値をPairing Registryへ保存しない

## 10. Season 0受入条件

- mDNS広告の有無を`OBSERVED / NOT_OBSERVED`で記録できる
- mDNSがなくても完全一致IPから別runbookへ進める
- IPが変わってもinstrument identityとendpoint履歴を分離できる
- discovery結果だけでpairedまたはcapableにならない
- hostname衝突、IP再利用、identity不一致をfail closedにできる
- registryなしでも再探索可能で、registryが実機権限の正本にならない
- 生DBとprivate identifierがGitへ入らない

## 11. 初回観測結果

2026-07-17、`en0`の`192.168.0.18/24`から有界runbookを一回実行した。

- `_services._dns-sd._udp`: 12 service typeを観測
- `_http._tcp`: 計測器ではない広告1件
- `_lxi._tcp`: 0件
- `_vxi-11._tcp`: 0件
- `_scpi-raw._tcp`: 0件
- `_scpi-telnet._tcp`: 0件
- SSDP: 23 datagram、応答元は`192.168.0.1`と`192.168.0.163`
- 対象候補`192.168.0.210`からのSSDP応答: 0件
- TCP、HTTP、SCPI、port scan: 0件

これはBonjour/mDNSがsegment上で機能している一方、3秒/service typeの窓で計測器向け広告を
`NOT_OBSERVED`とした記録である。SDS1204X-EのmDNS非対応を断定しない。次の候補はユーザー確認済み
exact IPへの別query-only runbookであり、本観測から自動接続しない。

### Machine-translation guardrail (en-US)

Bonjour is an implementation of mDNS/DNS-SD, not a separate competing discovery protocol. SDS1204X-E
mDNS advertisement is currently unverified. Discovery records are untrusted sightings, not paired identity
or instrument authority. The local SQLite registry tracks stable instrument identity separately from mutable
IP addresses and hostnames; pairing requires query-only identity evidence and explicit user confirmation.
