"""実験前ゲートとruntime境界のテスト。"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from psycho_py800mcp.gates import (  # noqa: E402
    GateClosedError,
    current_gate_status,
    require_instrument_io,
)
from psycho_py800mcp.main import main  # noqa: E402


class ExperimentGateTest(unittest.TestCase):
    """実験ゲートがfail-closedであることを確認する。"""

    def test_gate_is_closed(self) -> None:
        """Phase 0では実機I/Oを許可しない。"""

        status = current_gate_status()
        self.assertEqual(status.experiment_gate, "closed")
        self.assertFalse(status.instrument_io_allowed)

    def test_instrument_io_is_rejected(self) -> None:
        """ApprovalSession未確立時の実機I/O要求を拒否する。"""

        with self.assertRaises(GateClosedError):
            require_instrument_io()

    def test_mcp_service_is_rejected(self) -> None:
        """MCPサービス起動がsocket生成前に拒否される。"""

        self.assertEqual(main(["serve-mcp"]), 3)

    def test_presentation_runtime_has_no_instrument_authority(self) -> None:
        """プレゼンテーション層が実機権限を宣言しない。"""

        process = subprocess.run(
            [sys.executable, str(REPOSITORY_ROOT / "presentation" / "main.py")],
            check=True,
            capture_output=True,
            text=True,
        )
        status = json.loads(process.stdout)
        self.assertFalse(status["instrument_io_allowed"])
        self.assertEqual(status["accepted_input"], "artifact_id_only")


if __name__ == "__main__":
    unittest.main()
