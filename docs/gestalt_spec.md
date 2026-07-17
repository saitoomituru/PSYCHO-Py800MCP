# gestalt_spec.md — ゲシュタルト係数仕様

状態: `[REVIEW]` — メタGUI責務は設計済み。数値重みと閾値は未確定。

---

## 概念

PSYCHO-PASSの「犯罪係数」に対応する、現場状態のメタGUI用projection。
技術を専門としない管理者、人事、出資者、現場責任者へ、作業mode、監査状態、未確認事項、
必要人員を瞬間的に伝える。安全計算、実行許可、規格適合判定そのものではない。

人間が成立させたプローブ内容や画面数値をAIが読む場合は`OBSERVING`であり、人間の目視・転記支援に
相当する。そこからAIが自動検査を起動する、または入力経路を破壊方向へ変更する計画へ移るときに、
責任者、監査、二者確認、増員要求を前面へ出す。

## 権威境界

- 技術ゲート: `hazard_delta`、Dev Check、Engineer Check、MeasurementPlan、ApprovalSession
- メタGUI: 技術ゲートの状態を係数、状態語、アイコン、必要人員へ圧縮表示
- 禁止: 係数値から承認、許可、規格適合、安全性を逆算する
- 禁止: `UNKNOWN`を他項目との平均で消す
- 必須: 数値から根拠snapshotと担当者へdrill-downできる
- 必須: 決定役割、RiskSignal、BenefitSignalを別項目で表示する
- 禁止: 技術上の担当者を法的賠償責任者と自動推定する
- 禁止: 高リスクという理由だけで高ベネフィット作業を自動却下する
- 禁止: 係数を円、確率、事故率、損害額、ROI、時価総額へ変換する

---

## 旧計算式

```
ゲシュタルト係数 =
    voltage_unknown      × 40   # 電位が不明
  + gnd_not_isolated     × 80   # GNDアイソレート未確認
  + voltage_over_50v     × 100  # 旧暫定値。AC/DC・実効値・絶対値を含め再設計する
  + confidence_low       × 60   # スケマティック信頼度 < 0.5
  + adjacent_net_risk    × 30   # 隣接ネットに高リスクネットあり
  + protocol_unanalyzed  × 20   # デジタルプロトコル未解析

旧文書上の表記最大値: 500
```

現行の真偽値重みをすべて足しても330であり、400以上のcriticalへ到達できない。
また、`unknown`を単なる加点として扱う設計は廃止し、独立したfail-closedゲートへ移す。
Phase 0でモデルを再設計するまで、この計算式を実装しない。

## 現行表示モデル

数値式を固定する前に、最低限次の状態語を正本とする。色だけに依存せず、語句とアイコンを併記する。

| mode | 非専門者向け表示 | 人員メッセージ | 実行権限への影響 |
|---|---|---|---|
| `OBSERVING` | 観測・記録支援中 | 現在の担当者で継続 | なし |
| `ANALYZING` | 保存データ解析中 | 追加の物理担当不要 | なし |
| `PLAN_REVIEW` | 自動検査の計画監査中 | 計画責任者・監査者を表示 | なし |
| `TWO_CHECKS_REQUIRED` | 測定開始前の現物確認待ち | Dev＋Engineerが必要 | 未充足ならblock |
| `APPROVED_EXECUTION` | 承認済み計画を実行中 | 現在stepの担当を表示 | 技術ゲートに従う |
| `HIGH_RISK_OPERATION` | 高リスク作業・増員推奨 | 必要人数と役割を表示 | 技術ゲートに従う |
| `STOPPING_OR_BLOCKED` | 中止・縮退・未確認 | 新規操作禁止を表示 | block |

係数はこれらの状態を並べ替えや通知へ使う派生値であり、単独表示しない。たとえば大きな数字の横へ
「観測のみ」「計画監査待ち」「人員2名必要」「UNKNOWN 2件」を明記する。

### 影響の雰囲気表示

非専門の意思決定者向けには、次を`low / medium / high / unknown`等の順序カテゴリと短い理由で出す。

- instrument / probe / DUT replacement
- downtimeとlab interruption
- retest、再校正、失われるデータとschedule
- incident responseの複雑さ
- third-party property / service impact
- 追加人員と追加確認の重さ

各値はreason code、入力source、時点、confidenceを持つ。円、確率、損害額、保険支払額、会計引当、
時価総額への寄与を生成しない。正式な財務資料が別途存在する場合も、係数へ混ぜず参照IDだけを置く。

### ベネフィット表示

RiskSignalと同じ画面に、欠陥検出、手戻り回避、開発学習、測定証拠、schedule短縮、再利用性、
milestone・事業上のoption等を`BenefitSignal`として順序カテゴリと理由付きで表示する。Benefitを
期待金額、ROI、企業価値へ変換しない。

高リスク・高ベネフィットは「中止」ではなく「人員・予算・checkを追加して判断」へmappingする。
低リスク・低ベネフィットは優先度見直し、高リスク・低ベネフィットは再設計・延期候補、低リスク・
高ベネフィットは通常フロー候補とする。ただし`UNKNOWN`は四象限へ押し込まず独立表示する。

### 二軸スコア

- `ExecutionRiskScore`: 提案された執行が持つriskのプレゼンテーション値
- `EvidenceValueScore`: 取得データ量ではなく、意思決定・品質管理・再利用可能な証拠への寄与価値

暫定GUI profileでは両方を0〜300の順序メタ係数へmappingし、`scale_kind=ordinal_metaphor`、profile ID、
算出理由を必ず表示する。値の差や比に物理量・金額としての意味はない。旧0〜500式とは
互換でなく、自動換算しない。閾値は実測runと運用レビュー前の`PROVISIONAL`であり、実行ゲートに使わない。

数値の横には必ず自然言語ガイダンスを表示する。`EvidenceValueScore=50`はデータが50件という意味ではなく、
主として安心材料に留まる等の価値分類を表す。

---

## 旧係数レベルと対応アクション

次表は初期案の履歴であり、現在の権限表ではない。「即時執行可」は撤回済みで、実装へ転記しない。
ゲシュタルト係数はDev CheckまたはEngineer Checkを代替せず、低い係数でもAIによる測定開始と
入力経路変更を許可しない。

現行設計は絶対スコアより、確認済みbaselineから次操作が破壊方向へ動くかという`hazard_delta`を
優先する。低スコアでも破壊方向なら承認対象、副作用が不明なら破壊方向候補としてfail closedにする。

| 係数 | レベル | 音声 | 必要装備 | アクション |
|------|--------|------|---------|-----------|
| 0-99 | normal | 通常 | 通常プローブ | 旧案: 即時執行可（撤回） |
| 100-299 | recommend | 通常 | 差動プローブ推奨 | 推奨表示のみ |
| 300-399 | required | 警告 | 差動プローブ必須＋高圧モード | 装備確認後に執行 |
| 400-500 | critical | 変調警告 | 執行官2名＋差動＋高圧 | 監視官承認必須 |

---

## 音声出力例（eSpeak NG）

```
係数 347 の場合:
「たいしょうねっとのげしゅたるとけいすうは さんびゃくよんじゅうなな」
「こうあつおぺれーしょんを じゅんびしてください」
「さどうぷろーぶの そうちゃくをかくにんごのうえ スタートをおしてください」
```

この旧例は数値だけで装備を決めるため現行UIへそのまま採用しない。現行音声はmode、未充足check、
必要役割を読み上げる。

---

## 動作モードと係数精度

### フォワードモード（KiCadスケマティック読み込み済み）

- 電位: ネットリストから確定
- GNDアイソレート: トポロジー解析で判定
- 信頼度: 1.0（設計通りであれば）
- 係数精度: 高

### リバースモード（謎基板）

- 電位: Vision推定（信頼度0.3〜0.9）
- GNDアイソレート: 不明 → デフォルトでフラグ立て
- 信頼度: Vision解析結果に依存
- 係数精度: 低（保守的に高めに出る）

リバースモードでは信頼度が低いため係数が高くなりやすい設計。  
ロジアナ・オシロで確認するたびに信頼度が上がり係数が収束する。

---

## 係数の更新タイミング

1. スケマティック読み込み時（初期係数）
2. 測定結果取得後（信頼度更新→係数再計算）
3. ユーザーが手動で情報を追加した時
4. ロジアナでプロトコル解析完了時

---

## 実装

`src/engine/gestalt.py`

```python
from dataclasses import dataclass

@dataclass
class NetRiskProfile:
    net_name: str
    voltage_known: bool = False
    estimated_voltage: float | None = None
    gnd_isolated: bool = False
    confidence: float = 0.0
    adjacent_high_risk: bool = False
    protocol_analyzed: bool = False

def calculate_gestalt(profile: NetRiskProfile) -> int:
    score = 0
    if not profile.voltage_known:
        score += 40
    if not profile.gnd_isolated:
        score += 80
    if profile.estimated_voltage and profile.estimated_voltage > 50:
        score += 100
    if profile.confidence < 0.5:
        score += 60
    if profile.adjacent_high_risk:
        score += 30
    if not profile.protocol_analyzed:
        score += 20
    return min(score, 500)
```
