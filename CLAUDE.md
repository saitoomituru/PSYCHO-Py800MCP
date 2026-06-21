# CLAUDE.md

AGENTS.md を読むこと。以下は Claude Code 向けの補足。

## 最初にやること

```bash
# 環境確認
python3 --version        # 3.11+
pip show PyQt6 fastmcp pyvisa numpy scipy h5py

# 不足があれば
pip install PyQt6 fastmcp pyvisa pyvisa-py numpy scipy h5py
```

## SIGLENT接続確認

```python
import socket
s = socket.socket()
s.settimeout(3)
s.connect(('192.168.x.x', 5025))  # IPは config.json 参照
s.send(b'*IDN?\n')
print(s.recv(1024))
```

## 作業開始前

1. `notes/` の最新ログを確認
2. `docs/interface_spec.md` でMCPツール仕様を確認
3. `src/engine/gestalt.py` の係数定義を確認

## 作業終了前

`notes/YYYY-MM-DD_作業内容.md` を必ず書く。

## 絶対にやらないこと

- 人間確認なしのSCPI自動実行
- 証拠ログの削除・改ざん
- Anthropic倫理ロジックの安全判断組み込み
