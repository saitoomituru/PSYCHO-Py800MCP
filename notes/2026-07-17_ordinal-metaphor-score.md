# 2026-07-17 係数を順序メタ表記へ変更

状態: `[DESIGNED]` `[SUPERSEDES]`

## 方針変更

- `[SUPERSEDED]` Dashboardがcurrency付きCostExposure rangeを生成する案は採用しない。
- `[SUPERSEDED]` Risk／Benefitを正式な定量財務エビデンスとして扱う案は採用しない。
- `[DESIGNED]` 二軸scoreは`scale_kind=ordinal_metaphor`の会話用メタ表記とする。
- `[DESIGNED]` 円、確率、事故率、損害額、ROI、賠償額、企業価値へ換算しない。
- `[DESIGNED]` 表示値にはreason code、profile ID、`UNKNOWN`を併記する。
- `[DESIGNED]` 正式な財務・契約資料はユーザー指定の外部decision documentとしてlinkできるが、
  係数へ混ぜず、本システムが評価額を生成したとは主張しない。

## Claim Boundary

この記録は係数の表示責務を順序メタ表記へ変更したことだけを主張する。scoreの妥当性、事故確率、
損害額、ROI、企業価値、賠償責任、財務判断の正しさを主張しない。

## 内観メモ

- `[POEM]` 犯罪係数は空気を一秒で共有する舞台装置であって、株価算定表ではない。数字にスーツを
  着せても、円マークまで背負わせない。

## 次回TODO

- [ ] score schemaへ`scale_kind=ordinal_metaphor`を必須化する
- [ ] currency、probability、ROI、valuation fieldの混入を拒否するoffline testを設計する
- [ ] reason codeから日本語ガイダンスを再現するfixtureを作る
