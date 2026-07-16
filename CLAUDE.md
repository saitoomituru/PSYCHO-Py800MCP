# CLAUDE.md

AGENTS.md を読むこと。以下は Claude Code 向けの補足。

## 最初にやること

```bash
# Phase 0の分離runtimeを作成
./scripts/bootstrap_runtime_envs.sh

# 実験ゲートが閉じていることを検証
./scripts/verify_pre_experiment.sh
```

依存をグローバルPythonへ直接インストールしない。ネゴシエーション層とプレゼンテーション層は
別venvを使い、数理解析はPhase 1以降のDockerサンドボックス候補として扱う。

## SIGLENT接続確認（別の明示承認後）

```python
# Phase 0では実行しない。
# query-only ApprovalSessionと実験ノートを確立してから実装する。
```

## 作業開始前

1. `notes/` の最新ログを確認
2. `docs/implementation_plan.md` の実験開始ゲートを確認
3. `docs/architecture/runtime-boundaries.md` のruntime境界を確認

## 作業終了前

`notes/YYYY-MM-DD_作業内容.md` を必ず書く。

## 絶対にやらないこと

- 人間確認なしのSCPI自動実行
- 証拠ログの削除・改ざん
- Anthropic倫理ロジックの安全判断組み込み
