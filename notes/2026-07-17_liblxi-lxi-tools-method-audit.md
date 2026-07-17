# liblxi / lxi-tools method audit記録

分類: `OBSERVED / INFERRED / PLANNED / UNKNOWN`
タグ: `[FACT] [LIMITED] [Layer A]`
日付: 2026-07-17

## 検証範囲

公開sourceの静的読解とHomebrew formula metadataの確認を行った。package install、build、dynamic load、
network packet送信、計測器接続、SCPI送信は行っていない。

## OBSERVED

- `liblxi 1.22`の公開APIは`init / discover / discover_if / connect / send / receive / disconnect`の7関数だった。
- protocol enumにはHiSLIPがあるが、接続実装はerrorを返す。
- `discover_if`のinterface指定はVXI-11だけに適用され、mDNSでは無視される。
- mDNS backendがbuildされなかった場合、結果なしでreturn 0する経路がある。
- `lxi_receive`はNUL終端せず、受信byte数を返す。
- `lxi-tools`はlibraryではなく、共通C sourceをCLIとGTK GUIへcompileする構成だった。
- CLIはdiscover、任意SCPI、screenshot、benchmark、Lua runを持つ。
- Lua layerは任意SCPI、sleep、clock、CSV log helperを持つ。
- screenshot pluginは24件あり、機種によって設定変更、instrument内file生成・読取・削除を行う。
- Siglent SDS pluginは`scdp`を送りBMPとして受信する実装だった。
- 調査hostはmacOS 15.7.7、`x86_64` Hackintoshだった。
- Homebrewは`liblxi 1.22`と`lxi-tools 2.8`を提供するが、調査hostには未導入だった。

## INFERRED

- `liblxi`はtransport SDKとして十分小さいが、structured error、version getter、safety classificationは
  PSYCHO側で補う必要がある。
- Pythonから直接loadするより、native observer sidecarへdynamic linkしてprocess isolationを保つ方がよい。
- `lxi-tools screenshot`を一括でquery-only扱いすると、設定変更やfile operationを見落とす。
- lxi-tools全体をincludeするより、機種profileと例外をborrow ledger付きで抽出する方が軽い。

## UNKNOWN

- `liblxi 1.22`が現在のHackintoshでbuild・load・discoverできるか。
- Apple Silicon native buildとHomebrew artifactの実動作。
- Windows native MSVC backendとして利用できるか。upstreamはCygwin/WSL2経路を持つが同値ではない。
- SDS1204X-E firmware条件で`scdp`がacquisition、buffer、設定へ与える副作用。

## PLANNED

- 実機I/O前にnative observerのJSON schemaとcompile-time allowlistを作る。
- 最初のinclude対象をinitialize、bounded discover、単発`*IDN?`、disconnectへ限定する。
- `liblxi`導入後、architecture、dynamic dependency、required symbolをoffline検査する。
- screenshotはLink実験と分け、副作用仮説を持つ別runbookにする。

## Claim Boundary

source上の実装とpackage提供を観測した。対象OS・architecture・実機での動作は観測していない。upstreamの
method名やtested listを、PSYCHOで安全に使用できる証拠へ読み替えない。

## Inner Memo

SDKは小さく、沼は入口ではなく分類にいた。七つの関数を呼べれば勝ちではあるが、二十四枚のscreenshot札には
画面を見る猫、設定を触る猫、機器内へfileを作って消す猫が同じ名前で入っている。舐めるべきはAPI表面より、
一枚ずつの足跡だった。

## TODO

- borrow ledgerのschemaと`THIRD_PARTY_NOTICES`配置をPhase 0文書へ追加する。
- native observerのoffline symbol audit testを設計する。
