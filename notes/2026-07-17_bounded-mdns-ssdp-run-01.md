# 実機試験記録: 有界Bonjour/mDNS・DLNA/SSDP探索01

状態: `[OBSERVED]` `[LIMITED]` `[Layer A]`  
Run ID: `20260717-mdns-ssdp-01`

## 検証範囲

- 対象: en0上のBonjour/mDNS service browse、DLNA/UPnP SSDP応答観測
- 対象segment: `192.168.0.0/24`
- 対象候補: `192.168.0.210`（ユーザーが実機画面で確認済みのlocal IP）
- 除外: TCP接続、HTTP取得、VXI-11接続、SCPI、`*IDN?`、subnet sweep、port scan、packet capture
- 中止条件: Bonjour API error、scope逸脱、10秒超/service、SSDP 64 datagram到達、例外

「DLAN」は本runではDLNA/UPnPのSSDP discoveryを意味するものとして実行した。

## 実験前の期待

- `[EXPECTED]` LXI/VXI-11/SCPI serviceが広告されていればBonjour browseで観測できる。
- `[EXPECTED]` 広告がなければ`NOT_OBSERVED`とし、非対応へ昇格させない。
- `[EXPECTED]` SSDPはrouter、media renderer等を返し得るが、計測器identityとはみなさない。

## 環境

- 観測開始UTC: `2026-07-17T01:44:32.035035Z`
- 最終観測UTC: `2026-07-17T01:44:50.434760Z`
- ローカルtimezone: `Asia/Tokyo (JST, UTC+09:00)`
- Git base: `9abcd1e282f3039822c24d7a6da5f71d3deebb68`
- 実行時worktree: discovery実装が未commitの状態。下記source hashで固定
- OS / host: macOS Darwin 24.6.0 / x86_64
- Python runtime: `.venv-negotiation`
- network interface: `en0`
- host local IPv4: `192.168.0.18`
- netmask: `255.255.255.0`
- local gateway: `192.168.0.1`
- オペレーター: ユーザーの明示指示を受けCodexが固定runbookを起動

### 実行source hash

- `discovery_observation.py`: `054a689a760ea3b5ca26dab28e6a0c66ed0a6df2df95395ab283e50fa816be11`
- `run_bounded_discovery.py`: `edbe3fc6c5d9c7cb84bb648fd1a2dc4b2a8ff6fe545be36d700e915dac93615b`
- `test_discovery_observation.py`: `137b05b56cf6a529619b78efd448aa4aad5a1a10e93430ee05cb4e1318416123`

## 実行権限

- authority type: `BoundedDiscoveryRunbook`
- runbook SHA-256: `61bbdb81f3efe5671b95f2061784ea8a606e3e7bd485fa4209f49378a84cead6`
- 人間の明示起動: 本turnの「探索をかけるテストケースを作ってテスト実施」指示
- Bonjour allowlist:
  `_services._dns-sd._udp`, `_lxi._tcp`, `_vxi-11._tcp`, `_scpi-raw._tcp`,
  `_scpi-telnet._tcp`, `_http._tcp`
- Bonjour上限: 3秒/service type、interface indexはen0へ固定
- SSDP送信: `239.255.255.250:1900`へ固定`M-SEARCH ssdp:all`を1 datagram
- SSDP上限: MX=1、受信3秒、最大64 datagram
- TCP / HTTP / VXI-11 / SCPI / port scan authority: `false`

## offlineテスト

- 9件成功
- 固定allowlist、port scan拒否、SSDP packet完全一致、header選別、Global IPv4のみ伏字、既存実験gateを確認

## 実行コマンド

```text
.venv-negotiation/bin/python scripts/run_bounded_discovery.py
  --interface en0
  --output-directory .local/discovery-runs/20260717-mdns-ssdp-01
  --confirmation-token <fixed-token>
  --bonjour-seconds 3
  --ssdp-seconds 3
```

## 観測事実

- `[OBSERVED]` `_services._dns-sd._udp`で12種類のservice typeを観測した。
- `[OBSERVED]` service catalogはAirPlay、Android TV remote、Apple remote、companion link、EPPC、
  Google Cast、RAOP、RFB、SFTP/SSH、SMB、SSH、OSCだった。
- `[OBSERVED]` `_http._tcp`は計測器ではない複合機広告1件だった。
- `[NOT_OBSERVED]` `_lxi._tcp`: 0件。
- `[NOT_OBSERVED]` `_vxi-11._tcp`: 0件。
- `[NOT_OBSERVED]` `_scpi-raw._tcp`: 0件。
- `[NOT_OBSERVED]` `_scpi-telnet._tcp`: 0件。
- `[OBSERVED]` SSDP応答は23 datagram、local sourceは`192.168.0.1`と`192.168.0.163`だった。
- `[OBSERVED]` SSDPではInternet Gateway、Media Renderer、DIAL、AVTransport、RenderingControl等を観測した。
- `[NOT_OBSERVED]` `192.168.0.210`をsourceとするSSDP応答はなかった。
- `[OBSERVED]` TCP接続、HTTP取得、VXI-11接続、SCPI送信、port scanは実行されていない。

## 未観測・取得不能

- `[NOT_OBSERVED]` SDS1204X-Eに対応すると識別できるBonjour service。
- `[NOT_OBSERVED]` SDS1204X-Eに対応すると識別できるSSDP response。
- `[UNKNOWN]` SDS1204X-EがmDNSを実装していないのか、別service typeなのか、広告停止中なのか、
  3秒窓で取り逃したのか。
- `[UNKNOWN]` mDNS hostname、VXI-11 endpoint、SCPI endpoint。今回resolveや接続を行っていない。

## 成果物

| artifact ID | origin | size | SHA-256 | 公開可否 |
|---|---|---:|---|---|
| `discovery_raw.json` | Bonjour API + SSDP raw | local file | `fd75c24964ce8303a031ec9a2219dfc39d1220e41a6b18be850779bc7abc3eef` | Git外 |
| `summary.json` | host-generated summary | local file | `f7920d0c9deeec9a54ed7939183e5bda74f2bc16bc0a7ec716eca98dde7c78e1` | Git外 |

Git外path: `.local/discovery-runs/20260717-mdns-ssdp-01/`

## 失敗・逸脱

- `[DEVIATION]` 実行時点では新規runbook sourceが未commitだった。Git baseと各source SHA-256を記録し、
  実行直後に同一内容をcommitする。
- `[LIMITED]` Bonjour観測は各service type 3秒であり、非対応判定には短い。
- `[LIMITED]` SSDP UUID/USN、MAC、未匿名化identifierは公開ノートへ転記していない。

## 考察・推論

- `[INFERRED]` 同一segmentで複数Bonjour serviceを観測できたため、host側Bonjour APIとen0上の
  mDNS観測経路は機能している。
- `[INFERRED]` 対象計測器については、現時点でBonjour優先探索だけに依存できない。
- `[PLANNED]` 次の低侵襲候補は、ユーザー確認済み`192.168.0.210`だけを対象とする別の
  query-only identity runbookである。

## Claim Boundary

本記録は、記載したinterface、segment、allowlist、時間窓で広告・応答を観測した事実だけを主張する。
SDS1204X-EのmDNS非対応、LXI非適合、network不通、SCPI不成立を主張しない。DLNA/SSDP応答機器を
SDS1204X-Eとは認定しない。

## 内観メモ

- `[POEM]` Bonjourの街灯は点いていたが、オシロは名札を出さなかった。迷子ではなく、まだ住所を
  本人確認していないだけ。次は地図を塗り潰さず、ユーザーが指した一軒だけ玄関の表札を読む。

## 次回TODO

- [ ] exact IP `192.168.0.210`向けquery-only runbookを完全固定する
- [ ] 送信byte、port、timeout、応答上限、中止条件を提示する
- [ ] `*IDN?`の副作用なしをvendor資料とcommand contractで再確認する
- [ ] 人間の明示起動前で停止する
