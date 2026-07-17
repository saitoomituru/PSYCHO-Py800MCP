# interface_spec.md — レイヤー間インターフェース仕様

状態: `[NEEDS-REVISION]` — 初期設計資料。現行の実装正本ではない。

この文書のMCPツール候補は、ApprovalSession、実行環境境界、Phase/Season分離より前に作成された。
[`implementation_plan.md`](implementation_plan.md)と
[`architecture/runtime-boundaries.md`](architecture/runtime-boundaries.md)に従って再設計するまで、
SCPI実装の入力仕様として使用しない。

---

## データフロー

```
Claude（指揮）
　↓ 自然言語指示
MCP Client（Claude Code / このチャット）
　↓ MCP protocol
PSYCHO-Py800MCP MCPサーバー（src/mcp/server.py）
　↓ SCPI / sigrok / OpenCV
実機ハード（SIGLENT・WebCam・顕微鏡）
　↓ 波形データ / 画像 / "device_not_responding"
MCPサーバー → NumPy解析 → 要約JSON
　↓
Claude（次の指示）
```

---

## 共通レスポンス形式

```python
{
    "status": "ok" | "error",
    "timestamp": "2026-06-21T08:32:10+09:00",  # JST
    "tool": "get_waveform_summary",
    "data": {...},          # status=ok 時
    "message": "...",       # status=error 時
    "evidence_id": "ev_xxx" # 証拠保全ID（全ツール共通）
}
```

---

## 計測器系ツール

### `get_waveform_summary(channel, duration)`

波形を取得して要約を返す。生データはHDF5に保存し、要約JSONのみClaudeに渡す。

```python
# 入力
channel: int          # 1-4
duration: float       # 秒

# 出力 data
{
    "vpp": 3.28,
    "vrms": 1.16,
    "freq": 1000.2,
    "period": 0.0009998,
    "dc_offset": 0.02,
    "noise_floor_mv": 12.3,
    "thd_percent": 0.8,
    "samples": 1000000,
    "hdf5_path": "evidence/ev_xxx.h5"
}
```

### `set_trigger(mode, level, slope, channel)`

```python
# 入力
mode: str    # "EDGE" | "PULSE" | "SLOPE" | "VIDEO"
level: float # V
slope: str   # "POS" | "NEG"
channel: int # 1-4
```

### `set_timebase(scale, window)`

```python
# 入力
scale: float  # 秒/div (例: 0.001 = 1ms/div)
window: float # 秒（Noneで自動）
```

### `set_vertical(channel, scale, offset)`

```python
# 入力
channel: int   # 1-4
scale: float   # V/div
offset: float  # V
```

### `capture_waveform(channel)`

生波形をHDF5に保存し、パスと要約を返す。

### `get_measurements()`

```python
# 出力 data
{
    "ch1": {"vpp": 3.3, "freq": 1000, "vrms": 1.17},
    "ch2": {"vpp": 0.0, "freq": None, "vrms": 0.001},
}
```

---

## 校正系ツール

### `calibrate_source(source)`

```python
# 入力
source: str  # "mac_lineout" | "function_gen" | "manual"

# 処理: 既知周波数のサイン波で補正テーブルを生成
# 出力 data
{
    "correction_table_path": "calibration/mac_lineout_20260621.json",
    "freq_points": [20, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000],
    "gain_db": [-0.1, -0.2, -0.1, 0.0, 0.1, 0.0, -0.3, -0.8, -1.2, -2.1],
    "phase_deg": [...]
}
```

### `apply_correction(correction_table_path)`

以降の全測定に補正テーブルを適用。

### `measure_thd(frequency, channel)`

```python
# 出力 data
{
    "fundamental_hz": 1000.0,
    "fundamental_db": 0.0,
    "harmonics": [
        {"n": 2, "freq_hz": 2000, "db": -42.3},
        {"n": 3, "freq_hz": 3000, "db": -48.1},
    ],
    "thd_percent": 0.8,
    "thd_n_percent": 0.9
}
```

### `sweep_frequency(start, stop, steps, channel)`

---

## スケマティック系ツール

### `load_schematic(path)`

KiCadスケマティックを読み込んでフォワードモードに入る。

```python
# 出力 data
{
    "nets": ["VCC", "GND", "TP3", "I2C_SDA", ...],
    "components": ["U1:STM32F103", "C1:100nF", ...],
    "mode": "forward"
}
```

### `check_probe_safety(channel, net, gnd_ref)`

```python
# 出力 data
{
    "gestalt_coefficient": 347,
    "level": "required",           # normal/recommend/required/critical
    "required_probe": "differential",
    "estimated_voltage": "230VAC",
    "warnings": ["GND not isolated", "Adjacent 230V net"],
    "instruction": "差動プローブを使ってStartを押してください"
}
```

### `get_net_info(net_name)`

### `update_schematic_confidence(net, score)`

リバースモード用。信頼度スコアを更新。

---

## 映像系ツール

### `capture_webcam(device)`

```python
# 入力
device: int | str  # 0, 1, "/dev/video0"

# 出力 data
{
    "image_path": "evidence/ev_xxx_cam.jpg",
    "width": 1920, "height": 1080
}
```

### `capture_microscope(device)`

### `analyze_board_image(image_path)`

Vision解析で暫定スケマティックを生成（リバースモード）。

```python
# 出力 data
{
    "components": [
        {"id": "U1", "type": "MCU", "confidence": 0.85, "location": [120, 340]},
        {"id": "C1", "type": "capacitor", "confidence": 0.72, "location": [180, 290]},
    ],
    "nets_estimated": [...],
    "mode": "reverse",
    "overall_confidence": 0.61
}
```

---

## 証拠保全系ツール

### `start_evidence_log(session_id)`

### `log_approval(user, mode, action)`

```python
# 入力
user: str    # "enforcer" | "inspector" | username
mode: str    # "local" | "remote"
action: str  # "start_capture" | "set_trigger" | ...
```

### `save_anomaly_data(timestamp, data)`

異常検出時に自動呼び出し。手動呼び出しも可。

---

## ゲシュタルト係数計算式

```
coefficient =
    voltage_unknown      × 40   (電位不明)
  + gnd_not_isolated     × 80   (GNDアイソレート未確認)
  + voltage_over_50v     × 100  (推定電圧 > 50V)
  + confidence_low       × 60   (信頼度 < 0.5)
  + adjacent_net_risk    × 30   (隣接ネット干渉リスク)
  + protocol_unanalyzed  × 20   (プロトコル未解析)

Max: 500
```

| 範囲 | レベル | 指示 |
|------|--------|------|
| 0-99 | normal | 旧案: 通常プローブ、即時執行可（撤回。現行権限へ使用禁止） |
| 100-299 | recommend | 差動プローブ推奨 |
| 300-399 | required | 差動プローブ必須＋高圧モード |
| 400-500 | critical | 執行官2名体制・監視官承認必須 |
