# 2026-07-17 Phase 0 runtime境界と実験前骨格

状態: `[FACT]` `[Layer A]` `[LIMITED]`

## 検証範囲

- 対象: 文書上のPhase/Season分離、実験記録契約、ネゴシエーション／プレゼンテーションruntime境界
- 対象: Python 3.11の独立venv生成、実験ゲート、MCP composition rootの構造検証
- 除外: 実機IP探索、TCP接続、VXI-11、mDNS/LXI、USB列挙、SCPI送信、波形取得
- 除外: FastMCP、PyVISA、NumPy、SciPy、h5py、描画ライブラリの導入

## 観測事実

- `[OBSERVED]` ローカルにはPython 3.11.14と`uv`が存在した。
- `[OBSERVED]` `.venv-negotiation`と`.venv-presentation`をPython 3.11.14で別々に生成した。
- `[OBSERVED]` 両runtimeのlockfileは第三者依存ゼロで生成された。
- `[OBSERVED]` ネゴシエーション層の`status`は`experiment_gate=closed`、
  `instrument_io_allowed=false`を返した。
- `[OBSERVED]` プレゼンテーション層は`instrument_io_allowed=false`、
  `accepted_input=artifact_id_only`を返した。
- `[OBSERVED]` 標準ライブラリによる境界テスト4件が成功した。
- `[OBSERVED]` `serve-mcp`は実験ゲートで拒否され、終了コード3を返した。
- `[OBSERVED]` `src/.DS_Store`をGit indexから外し、再追跡しない規則を追加した。

## 生成・更新した正本

- `README.md`
- `AGENTS.md`
- `CLAUDE.md`
- `docs/implementation_plan.md`
- `docs/architecture/runtime-boundaries.md`
- `notes/AGENTS.md`
- `notes/experiment-template.md`
- `main.py`
- `src/psycho_py800mcp/`
- `presentation/main.py`
- `runtimes/negotiation/`
- `runtimes/presentation/`
- `scripts/bootstrap_runtime_envs.sh`
- `scripts/verify_pre_experiment.sh`
- `tests/test_experiment_gate.py`

## Git保全

- `[OBSERVED]` `e9daa8c` — `[docs] PhaseとSeasonの実装・実験計画を再構成`
- `[OBSERVED]` `4294471` — `[eng] runtime: ネゴ層とプレゼン層の実験前境界を追加`
- `[OBSERVED]` 上記2コミットを`origin/main`へpushした。

## 未観測・取得不能

- `[NOT_OBSERVED]` SDS1204X-EのIP、`*IDN?`応答、firmware、serialは取得していない。
- `[NOT_OBSERVED]` CH1の公称1 kHz基準信号はソフトウェアから観測していない。
- `[NOT_OBSERVED]` 波形バイナリ、CSV、画像成果物は生成していない。
- `[UNKNOWN]` query-only通信時に必要となる装置状態照会コマンドの最終allowlistは未確定。

## 失敗・逸脱

- `[DEVIATION]` サンドボックス内の通常権限では外部リポジトリに`__pycache__`を作れず、
  構文検証を許可済み権限で再実行した。コードの構文エラーではない。
- `[FAILED]` 物理実験は試行していないため、該当なし。

## Claim Boundary

この記録が主張するのは、記載したコミットでPhase 0の文書とruntime骨格を作り、ローカルの
Python 3.11.14環境で実験ゲートの境界テスト4件が成功したことだけである。SDS1204X-Eとの
通信、MCPサービス稼働、波形取得、描画、数理解析の成立を主張しない。

## 内観メモ

- `[POEM]` 物理層へ触る前に「まだ触っていない」をコードとログの両方で示せる床ができた。
  実機の眼を開く前に、まぶたが閉じていることをテストできる状態になった。

## 次回TODO

- [ ] query-only ApprovalSessionの対象機器、コマンドallowlist、TTL、中止条件を確定する
- [ ] Git外のRunArtifact保存先と公開用正規化経路を確定する
- [ ] Season 0最初の実験ノートを`notes/experiment-template.md`から作成する
- [ ] 人間が送信予定コマンドを確認した後、実験ゲートを開く変更を別コミットにする
- [ ] 固定IP Socketによる`*IDN?`実験へ進む
