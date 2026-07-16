# gestalt_spec.md — ゲシュタルト係数仕様

状態: `[NEEDS-REVISION]` — 重みと閾値は再設計前。実装へ転記しない。

---

## 概念

PSYCHO-PASSの「犯罪係数」に対応する、  
電気回路ネットの定量的リスクスコア。

「感覚」でプローブを当てるのではなく、  
スケマティック情報・測定履歴・安全規格に基づいて  
数値でリスクを提示する。

---

## 計算式

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

---

## 係数レベルと対応アクション

| 係数 | レベル | 音声 | 必要装備 | アクション |
|------|--------|------|---------|-----------|
| 0-99 | normal | 通常 | 通常プローブ | 即時執行可 |
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
