# Bounded Measurement EnvelopeとAUTO Dev cycle

日時: 2026-07-17  
記録状態: `DESIGNED` / `INFERRED`  
実機操作: なし

## 背景

自動測定で垂直感度、offset、coupling等を一操作ごとに承認させると、実用的な反復測定にならない。
一方、無信号を捕捉したAUTOがrange探索を続けると、起動前、配線不成立、保護relay開放中、想定外DCを
区別できないまま入力条件を動かす可能性がある。

audio amplifierでは電源投入から安全relay接続までの間にDC spikeまたはoffsetが存在し得る。そのため、
定常波形だけを根拠に入力rangeを承認すると、起動過渡をenvelope外へ落とす。

## 決定

- 承認単位をSCPI commandごとでなく、不変な`MeasurementEnvelope`とplan hashにする。
- ADC／入力front endの最終安全rangeを`PhysicalExposureEnvelope`としてユーザーへ提示・承認する。
- `ObservationWindowPolicy`内のtimebase、sample rate、memory depth、pre-trigger、確認済みbandwidth limit、
  FFT帯域はAIが自動選択できる。
- 低周波漏れや音響帯域外の1-bit DSD noise探索を、垂直入力rangeの再承認と混同しない。
- voltage、transient、frequency、probe、coupling、impedance、physical GND、DUT／source stateを固定する。
- envelope内の反復は都度承認不要だが、AIはenvelopeを自己拡張できない。
- `NOT_OBSERVED`と`UNKNOWN`はAUTO継続条件でなく`HOLD_AND_REPLAN`条件とする。
- 人間直接AUTOとAI遠隔AUTOを分ける。AI遠隔AUTOは複合状態変更としてPhase 2まで閉じる。
- Season 0では既存artifactと設定snapshotから`AUTOSET_PROPOSE`だけを生成し、実機へAUTOを送らない。
- audio amplifierは`POWER_OFF`、`POWER_ON_RELAY_OPEN_TRANSIENT`、`RELAY_CLOSE_TRANSITION`、
  `STEADY_STATE`、`POWER_OFF_TRANSIENT`へ分ける。
- scopeのSTOP／arm、DUT電源、relay接続を別stepにし、曖昧な`start`へ束ねない。
- 限定周回を`ACQUISITION_STOPPED -> DUT_RESTART_REQUESTED -> SETTLING -> AUTOSET_ONCE ->
  ENVELOPE_VALIDATION`として記録する。
- 認可最大rangeで成立しなければ`RANGE_EXHAUSTED / INCONCLUSIVE`とし、追加探索を停止する。
- 部分artifactとlogを確定・handoffした後は`READ_ONLY_HANDOFF`へ移る。

## 根拠

SIGLENT公式の[SDS1000X-E User Manual](https://siglentna.com/download/22002/)では、Auto Setupが垂直scale、
水平timebase、trigger modeを自動調整する機能として説明される。公式の
[Oscilloscope Programming Guide](https://siglentna.com/download/17013/)にもAUTOSET／`ASET`が複数設定を
変更するcommandとして記載される。したがってAI遠隔AUTOをquery-onlyに分類しない。

## Claim Boundary

- `[DESIGNED]` 文書上の承認envelope、AUTO停止条件、アンプ状態機械を定義した。
- `[OBSERVED]` 公式資料のAUTO／AUTOSET説明をローカルで閲覧した。
- `[UNKNOWN]` SDS1204X-E実機で`ASET`が変更する全設定、rollback可能性、無信号時挙動。
- `[UNKNOWN]` 対象audio amplifierの実際の起動過渡、relay timing、DC spike値。
- 本記録ではSCPI、VXI-11、HTTP、TCP接続、AUTO、RUN、STOP、DUT電源操作を実施していない。

## 次の実験前ゲート

1. query-onlyで現在設定と既存bufferを取得できる機種契約を確定する。
2. `MeasurementEnvelope` schemaとoffline validatorを実装・unit testする。
3. `NOT_OBSERVED`／`UNKNOWN`からrange拡張commandが生成されないことを回帰testする。
4. `RANGE_EXHAUSTED`からpartial finalizeとread-only handoff以外へ遷移できないことをtestする。
5. AUTO実機試験はPhase 2のDev Check、Engineer Check、ApprovalSession完成後に別runbookで行う。

### Machine-translation guardrail (en-US)

Approval covers a bounded and immutable measurement envelope, not unrestricted range search. A no-signal or
unknown-signal result must hold the current approved state and return for replanning. Human-direct autoset is
outside PSYCHO's AI approval path; AI-triggered autoset is a composite state-changing operation. Startup
transients and relay-open states must not be mistaken for steady-state measurements.
