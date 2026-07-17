# 承認比例原則・Local Bench Trust・SaaS型責任回避境界

分類: `OBSERVED / INFERRED / PLANNED`  
日付: 2026-07-17

## OBSERVED

- ユーザーは、人間がlxi-gui等を直接操作する経路とAI starterを分離するよう要求した。
- すでにprobe、trigger、RUN、波形表示が成立した後の解析へ過剰な権限管理を持ち込まないよう要求した。
- NATを跨がないlocal segmentの機種logとIPを、credential同様に過剰秘匿しない方針が提示された。
- SaaSが免責目的で包括拒否する挙動へ釘を打つ必要が提示された。

## INFERRED

- 操作主体とhazard deltaを独立に扱うと、人間GUIへAI承認を誤適用せず、AIによる物理変更だけを閉じられる。
- local storageとpublic exportを分離すれば、内部証拠を残しながら公開範囲を選べる。
- blockをcapability単位にすると、危険操作を止めながらread-only解析を継続できる。

## PLANNED

- `LOCAL_BENCH / AUTHENTICATED_LAN / ROUTED_OR_WAN`のsecurity profileを実装する。
- block responseへspecific hazard、missing evidence、how to proceed、allowed nowを必須化する。
- 人間操作由来artifactとAI操作由来runをprovenanceで区別する。

## Claim Boundary

人間GUIの安全性、local LANの絶対安全、認証不要を一般化しない。現在対象のlocal bench運用に比例した
defaultを設計しただけであり、WAN、共有lab、credential付き機器は別profileへ移す。

## Inner Memo

鍵を掛けるべき扉に鍵を掛け、窓から見えている波形に毎回通行手形を要求しない。免責の城壁で現場を
囲うのではなく、燃える方向のレバーだけを止め、読めるログと帰れる道を残す。
