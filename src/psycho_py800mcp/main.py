"""ネゴシエーション層CLI。"""

from __future__ import annotations

import argparse
import json
import logging
from collections.abc import Sequence

from .gates import GateClosedError, current_gate_status
from .help_api import get_agent_help
from .mcp_service import serve_mcp


LOGGER = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """実験前CLIの引数パーサーを構築する。"""

    parser = argparse.ArgumentParser(prog="psycho-py800mcp")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status", help="実験ゲートとruntime境界を表示する")
    subparsers.add_parser("serve-mcp", help="MCPサービスを開始する（現在はゲートで拒否）")
    help_parser = subparsers.add_parser("help", help="接続AI向けオシロ虎の巻を表示する")
    help_parser.add_argument(
        "--format",
        choices=("markdown", "fam_json", "bundle"),
        default="bundle",
        dest="response_format",
    )
    subparsers.add_parser(
        "serve-help-mcp",
        help="実機権限を持たないAI HELP専用MCPをstdioで開始する",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """CLIを実行し、プロセス終了コードを返す。"""

    args = build_parser().parse_args(argv)
    if args.command == "status":
        print(json.dumps(current_gate_status().to_dict(), ensure_ascii=False, indent=2))
        return 0

    if args.command == "serve-mcp":
        try:
            serve_mcp()
        except GateClosedError as exc:
            LOGGER.error("experiment_gate_closed: %s", exc)
            return 3

    if args.command == "help":
        print(
            json.dumps(
                get_agent_help(response_format=args.response_format),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.command == "serve-help-mcp":
        from .help_mcp_server import serve_help_mcp

        serve_help_mcp()
        return 0

    return 2
