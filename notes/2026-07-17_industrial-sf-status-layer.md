# 2026-07-17 産業ステータス核とSF外皮

状態: `[DESIGNED]` `[Layer A]`

## 設計判断

- `[DESIGNED]` 青／黄／赤／灰黒のproject-local status lampをsemantic coreにする。
- `[DESIGNED]` 青は観測、黄は追加確認員、赤は停止・復旧対応体制、灰黒はunknown blockを表す。
- `[DESIGNED]` 色状態はoperation snapshotへ付与し、人間へ付与しない。
- `[DESIGNED]` 個人別係数、ランキング、賠償責任表示を禁止する。
- `[DESIGNED]` 走査線、オーラ、係数、音声は交換可能なSF themeとし、技術ゲートを変更しない。
- `[DESIGNED]` Dashboardを事故後の犯人探しでなく、事故前のstaffing・recovery readiness要請へ使う。

## Claim Boundary

この記録はGUIのsemanticとanti-blame境界を設計したことだけを主張する。色mappingの規格適合、GUI実装、
事故低減、人員配置の有効性、実機安全性を主張しない。

## 内観メモ

- `[POEM]` 枯れた三色灯は火事になる前に人を呼ぶ。そこへSFのオーラを被せるのは、偉い猫の視線を
  現場へ向けるため。赤く染めるのは人ではなく、これから踏む手順である。

## 次回TODO

- [ ] plain industrial viewとSF themeが同じsnapshotを描くcontractを設計する
- [ ] color-blind、monochrome、mute時の識別testを設計する
- [ ] person IDをscore payloadへ混入させないschema testを設計する
