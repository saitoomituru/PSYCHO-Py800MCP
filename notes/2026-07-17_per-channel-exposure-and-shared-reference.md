# Channelごとの物理曝露と共有reference境界

日時: 2026-07-17  
記録状態: `DESIGNED` / `INFERRED`  
実機操作: なし

## 決定

- instrument全体で一つのrangeを承認せず、各CHへ`ChannelExposureContract`を持たせる。
- Vrms、Vpeak、DC、offset、transient、probe、BNC到達値、coupling、impedance、V/div、node、referenceを固定する。
- 小さすぎるV/divによる表示飽和と、probe／BNC／common-mode定格超過を別reason codeにする。
- 全CHのground／earth／floating関係を`SharedReferenceContract`で組合せ検証する。
- math subtractionは差動probeや絶縁測定の代用品にしない。
- preamp、真空管plate、output transformer二次側、dummy loadを別measurement pointとして扱う。
- optimizerは各CH契約と共有reference契約の積集合内だけを探索する。
- 物理接続graphはAI推論でなくエンジニアの`EngineerProbingDeclaration`を正本にする。
- isolation transformerの有無だけでなく、scope、source、DUT、dummy load、USB／LANによる再接地も確認する。
- 宣言不足時はAI起点writeを閉じるが、既存波形のread／解析は`UNKNOWN`付きで許可する。
- 承認UIでrange、probe、GND、coupling、impedance等が合わなければユーザーが`REJECTED_FOR_REPLAN`を返す。
- AIはreject理由を入力に新plan hashを作り、旧承認を流用せず再提出する。
- 承認後のprobe倍率／GND等の変更はwrite bindingを失効させるが、既存dataのreadは止めない。

## 例のClaim Boundary

speaker lineが`50 VAC`と表現されても、それだけではRMS、peak、波形crest factor、transient、reference、probe倍率、
BNC到達値を確定できない。`50 mV/div`が即ADC損傷になるとも断定しない。明らかな表示range不一致は実行前に
拒否し、物理損傷可能性はprobeとscopeの周波数条件付き定格、common-mode、接地から別判定する。

真空管plateの約240 Vと、output transformer二次側4 ohm dummy load上の最大電圧を同じrangeへ束ねない。
二次側は承認された出力上限と負荷条件から計算し、一次側は高電圧probe、common-mode、接地、過渡、実配線の
確認を別途要求する。本記録は対象amplifierの実測値、probe適合性、安全な接続成立を主張しない。

## 公式資料から確認した境界

- SIGLENT公式datasheetはSDS1000X-Eの入力上限を周波数条件付きで示しており、V/divとは別仕様である。
- SIGLENT公式manualは計測器を保護接地し、signal referenceを高電位へ接続しないよう警告している。
- Tektronix公式floating measurement資料は、一般的なbench scopeがchannel間でearth referenceを共有し得ることを
  説明している。

参照:

- [SDS1000X-E Datasheet](https://siglentna.com/wp-content/uploads/dlm_uploads/2024/06/SDS1000X-E_DataSheet_EN04G.pdf)
- [SDS1000X-E User Manual](https://siglentna.com/wp-content/uploads/2020/04/SDS1000X-E_UserManual_UM0101E-E03C.pdf)
- [Fundamentals of Floating Measurements](https://download.tek.com/document/3AW_19134_2_MR_Letter.pdf)

### Machine-translation guardrail (en-US)

Each analog channel requires its own approved physical-exposure contract, and all channels require a shared-reference
check. Display scale mismatch and electrical input-rating violation are separate conditions. A mathematical channel
subtraction does not provide galvanic isolation or make unsafe ground connections acceptable.
The physical connection graph must come from an engineer's on-bench declaration; AI may validate it but must
not invent isolation, shared-ground, or differential-probe facts. Missing declarations block AI-originated
instrument writes, not read-only analysis of an already established waveform.
