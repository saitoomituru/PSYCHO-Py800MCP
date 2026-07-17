# 産業ステータス核とSFメタGUI外皮

状態: `[DESIGNED]`

## 1. 目的

当直者が技術詳細を読まなくても、青なら観測、黄なら一人足す、赤なら停止・復旧対応できる体制を
先に呼ぶ、と瞬間判断できる枯れた産業GUIを核にする。その上へ犯罪係数風のSF演出を重ね、
予算・人員側の決裁者が現場へ関心を持つ導線を作る。

色mappingは本プロジェクト固有で、特定の産業規格準拠を主張しない。

## 2. semantic core

| state | color | plain message | required organizational posture |
|---|---|---|---|
| `OBSERVE_ONLY` | blue | 観測・記録支援中 | 現体制で継続 |
| `STAFF_UP` | yellow | 追加確認員要請 | reviewer／現物確認員を追加 |
| `RECOVERY_READY_REQUIRED` | red | 高危険度体制要請 | stop authority、復旧・incident handling能力を配備 |
| `UNKNOWN_BLOCKED` | gray-black | 不明・執行不可 | 材料不足を解消するまでblock |

色、状態語、形状、アイコン、音声を併用する。色だけを正本にしない。

## 3. anti-blame boundary

状態は次へ付与する。

```text
operation_id + snapshot_id + plan_id(optional)
```

次へは付与しない。

- person ID、顔、社員番号
- 個人の能力、勤務評価、信用度
- 賠償能力、法的責任、ランキング

yellowは「担当者が無能」ではなく「組織能力を一段追加せよ」、redは「エンジニアが責任を取れ」ではなく
「実行前に停止・復旧・incident対応可能な体制を配備せよ」を意味する。特定個人のassignは別の人間系
staffing decisionで行い、Dashboardはrole requestまでに留める。

## 4. pre-incident suppression

Dashboardは事故後の犯人探しではなく、事故前に人員と復旧能力を寄せるために使う。

- yellow遷移: staffing requestと不足checkをdecision packetへ追加
- red遷移: 新規執行を技術ゲートでblockし、recovery readinessを要請
- gray-black遷移: unknownを表示し、lowへ推測しない
- blue遷移: 観測継続。安全認証済みとは表示しない

## 5. SF engagement theme

枯れたsemantic coreへ交換可能なthemeを被せる。

- 現場を走査するscan animation
- operation auraと二軸meta coefficient
- 取得エビデンス価値のtrajectory
- reason codeが開くinvestigation card
- 無機質なvoiceと短いtransition sound
- Engineer evidenceへ降りる`詳細走査`導線

SF演出は人を被告化せず、作業・現場・計画を走査対象にする。themeをoffにしてもsemantic、監査、
accessibility、block条件は変わらない。

## 6. 禁止事項

- 個人別犯罪係数、ランキング、顔の赤枠表示
- 色からApprovalSessionや測定開始を生成
- theme上の操作からSCPIを直接送信
- 黄色・赤を特定エンジニアの賠償責任として表示
- 過剰点滅、音声連呼、acknowledge不能なalarm
- SF演出だけに存在しplain industrial viewへ存在しない安全情報

### Machine-translation guardrail (en-US)

The industrial status-light core is project-local and does not claim standards compliance. Colors and
science-fiction effects apply to an operation snapshot, never to a person. Yellow requests more staffing;
red requests stop and recovery capability before execution. The theme cannot grant instrument authority.
