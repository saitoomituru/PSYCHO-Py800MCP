# 2026-07-17 測定開始・入力経路変更の二者確認境界

状態: `[DESIGNED]` `[Layer A]` `[LIMITED]`

## 検証範囲

- 対象: 保存済み解析、既存取得読み取り、時間軸、測定開始、垂直入力経路の権限分離
- 対象: Dev CheckとEngineer Checkの役割分離
- 除外: 実機通信、SCPI送信、測定開始、設定変更、安全性の実証

## 設計判断

- `[DESIGNED]` 保存済みartifactの解析はMeasurementPlan承認不要とする。
- `[DESIGNED]` 既存buffer読み取りは、再armやbuffer clear等を伴わないと確認できた場合だけ承認不要とする。
- `[DESIGNED]` 時間軸変更はdata-quality操作として、垂直レンジ系の物理保護境界から分離する。
- `[DESIGNED]` AIによる測定開始と入力経路変更には、Dev CheckとEngineer Checkの両方を要求する。
- `[DESIGNED]` Dev Checkは設計想定範囲、Engineer Checkは現物の設計超過、GND loop、leakage、
  接続点、probe倍率、接地を確認する。片方で代用しない。
- `[DESIGNED]` 対象点、DUT、配線、probe、GND、入力経路が変われば二者確認を失効させる。
- `[DESIGNED]` 絶対リスクスコアではなく、確認済みbaselineから破壊方向へ動くかを`hazard_delta`で表す。
- `[DESIGNED]` 副作用が不明な操作は低リスクへ丸めず、破壊方向候補として二者確認側へ倒す。
- `[DESIGNED]` ユーザーが選択したObservationContext内の画面、既存buffer、camera、KiCad等の反復読取は
  都度承認を要求しない。観測ログは承認ではなく出自記録として残す。
- `[DESIGNED]` 非接触可動範囲内のカメラ移動は観測操作とし、DUTやprobeへ接触し得る場合だけ再分類する。

## Claim Boundary

この記録は権限分類を設計したことだけを主張する。コマンドの機種別副作用、SDS1204X-Eの安全性、
実電圧、GND loop、leakage、測定開始、入力経路変更の成立を主張しない。

## 内観メモ

- `[POEM]` 横軸を伸ばすのは時間の見え方を変える。縦の入口を切り替えるのは、眼そのものへ入る
  エネルギーの受け方を変える。同じ設定変更という箱へ押し込めない。

## 次回TODO

- [ ] capability enumと副作用metadataをschema化する
- [ ] 時間軸コマンドの機種別副作用をvendor原本で確認する
- [ ] Dev Check／Engineer Checkの失効条件をofflineテストへ落とす
