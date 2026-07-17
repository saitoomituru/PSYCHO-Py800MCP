# 不可逆性・技能代替禁止・外部data契約境界

分類: `OBSERVED / INFERRED / PLANNED / UNKNOWN`
タグ: `[FACT] [HYPOTHESIS] [Layer A]`
日付: 2026-07-17

## 検証範囲

ユーザー提示の目的関数と既存architecture文書を照合し、承認対象を不可逆な物理損傷へ集中させる設計境界を
整理した。実機操作、SCPI送信、range変更、manual記載値による限界計算は行っていない。

## OBSERVED

- ユーザーは、AIによるrange／input path変更がADCを破損方向へ遷移させる事故を最優先で防ぐよう要求した。
- 機器内data取得後の外部AI providerにおける保存・利用は、接続したユーザーとproviderの契約問題として
  PSYCHOの物理安全gateから分離する方針が提示された。
- GUI、容量、過去file、復元可能な設定は、commandとbaselineをloggingしてrestore可能性を残す方針が提示された。
- `AIとオシロが接続できる`ことを理由に、物理経験のない人へhardware作業を割り当てる組織事故を防ぐという
  目的が提示された。

## INFERRED

- ADCだけでなく入力front end、probe、DUT、source、GNDを同じ不可逆物理曝露群として扱う必要がある。
- reversible state、instrument storage、data egressを別classにすれば、物理gateを弱めず過剰承認を減らせる。
- Engineer Checkへexecutor本人の受諾と現物確認主体を含めると、AIやmanagerによる技能代替の誤認を防げる。
- 外部provider契約をscope外とする場合も、PSYCHO自身が実装するegressの宛先・範囲は明示する必要がある。

## UNKNOWN

- SDS1204X-Eの現在firmwareにおける各SCPI commandの入力経路副作用。
- 対象manual／規格書に基づく具体的な入力限界、probe derating、周波数依存条件。
- `scdp`がacquisition state、buffer、設定へ与える副作用。

## PLANNED

- `PHYSICAL_EXPOSURE_CHANGE`をrangeだけでなくimpedance、offset、coupling、probe、GND、sourceへ展開する。
- plan schemaへexecutor、executor acceptance、Dev Check主体、Engineer Check主体、不足resourceを追加する。
- reversible state／instrument storageへsnapshot、restore、cleanup logを追加する。
- MCP responseへegress destinationとreturned data scopeを記録する。

## Claim Boundary

本記録は設計境界であり、SDS1204X-Eの安全入力限界や特定commandの安全性を確定していない。具体値は
ユーザーが投入する対象manual／規格書と現物確認に基づき、MeasurementPlanごとに固定する。

## Inner Memo

AIをつないだことは、猫の手を一本増やしただけで、probeを握った手に経験を注入したことにはならない。
燃えたADCはundoできない。画面やfileは足跡を残せば戻せることが多い。だから門番は秘密っぽさではなく、
戻れない方向と、戻れる方向を見分けるために立たせる。

## TODO

- plan／ApprovalSession schema実装時にexecutor acceptanceをtest fixtureへ追加する。
- SDS1204X-E manual投入後、input path capabilityをfirmware条件付きで作成する。
