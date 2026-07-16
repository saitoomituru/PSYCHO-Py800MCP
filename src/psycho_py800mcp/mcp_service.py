"""MCPサービスcomposition root。"""

from __future__ import annotations

from typing import NoReturn

from .gates import require_instrument_io


def serve_mcp() -> NoReturn:
    """MCPサービスを開始する。

    Phase 0では実験ゲートを先に検証するため、FastMCPのimportやsocket生成へ到達しない。
    bootstrap実験とquery-only ApprovalSessionの仕様確定後に、サービス構築をこの関数へ接続する。
    """

    require_instrument_io()
    raise RuntimeError("MCP service adapter is not implemented")
