"""物理実験へ進む前のfail-closedゲート。"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


class GateClosedError(RuntimeError):
    """実験ゲートが閉じている状態で物理操作が要求されたことを示す。"""


@dataclass(frozen=True, slots=True)
class GateStatus:
    """現在の実験ゲート状態。"""

    phase: str
    season: str
    experiment_gate: str
    instrument_io_allowed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        """JSON化可能な辞書へ変換する。"""

        return asdict(self)


def current_gate_status() -> GateStatus:
    """Phase 0準備中の固定ゲート状態を返す。"""

    return GateStatus(
        phase="phase_0",
        season="season_0_preflight",
        experiment_gate="closed",
        instrument_io_allowed=False,
        reason="bootstrap query-only runbook has not been explicitly started",
    )


def require_instrument_io() -> None:
    """実機I/O許可を検証し、現段階では必ず拒否する。"""

    status = current_gate_status()
    if not status.instrument_io_allowed:
        raise GateClosedError(status.reason)
