# SDS1204X-E mDNS調査とPairing Registry設計

分類: `OBSERVED / INFERRED / PLANNED / UNKNOWN`  
日付: 2026-07-17

## 検証範囲

- 対象: 公開一次資料によるSDS1204X-EのLAN探索方式調査、実験前要件、local pairing DB
- 除外: LAN packet送受信、実機接続、SCPI、Web access、VXI-11 probe、subnet scan

## OBSERVED

- SIGLENT公式資料はSDS1000X-E系のVXI-11、Web、SCPI Socket 5025、Telnet 5024を記載する。
- 確認したSIGLENT User ManualとProgramming GuideにはmDNS、Bonjour、DNS-SDの明記を確認できなかった。
- LXI ConsortiumはLXI 1.3以降の適合deviceにmDNS service supportを要求している。
- 本調査では実機network trafficを発生させていない。

## UNKNOWN

- 対象SDS1204X-Eと現在firmwareがmDNS/DNS-SD広告を出すか。
- 広告する場合のservice type、instance、TXT、hostname、TTL。
- SIGLENT資料の「VXI-11 (LXI)」がどのLXI適合versionまたは実装範囲を意味するか。

## INFERRED

- VXI-11対応だけからmDNS対応を断定できない。
- mDNSを最初の有界観測にし、広告がなければユーザー確認済みexact IPへfallbackするのが低侵襲である。
- IPとhostnameは変化するため、機器identityとendpoint履歴をSQLiteで分離する必要がある。

## PLANNED

- mDNS観測runbookを固定し、人間の明示起動直前で停止する。
- query-only `*IDN?`と人間確認後にだけ`user_paired`へ昇格する。
- 生SQLite、IP、MAC、serialをGitへ保存しない。

## Claim Boundary

SDS1204X-EのmDNS対応、LXI適合、SCPI通信成立、identity field、Pairing Registry実装を主張しない。
本記録は公開資料調査と設計だけを記録する。

## Inner Memo

機械をIP番地へ縛ると、DHCPの引っ越しで魂と住所を取り違える。広告は呼び声、IPは今日の住所、
pairingは本人確認。三つを同じ列へ押し込まない。

## 次回TODO

- [ ] Git外のSQLite pathと`.gitignore`を準備する
- [ ] schema migrationとoffline unit testを実装する
- [ ] mDNS観測runbookを完全固定する
- [ ] 実験者へ送出範囲と中止条件を提示し、明示起動前で停止する
