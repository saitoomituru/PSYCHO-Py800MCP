#!/usr/bin/env python3
"""有界なBonjour/mDNSおよびDLNA/SSDP観測を起動する。"""

from __future__ import annotations

import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from psycho_py800mcp.discovery_observation import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
