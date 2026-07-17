"""実機権限を持たないAI HELP専用FastMCPサーバー。"""

from __future__ import annotations

import json
from typing import Any

from fastmcp import FastMCP

from .help_api import get_agent_help, list_agent_help_topics


mcp = FastMCP(name="PSYCHO-Py800MCP Agent Help")


@mcp.tool
def list_help_topics() -> dict[str, Any]:
    """接続AIが読めるproject-local HELP topicを列挙する。"""

    return list_agent_help_topics()


@mcp.tool
def get_help(
    topic: str = "oscilloscope_field_guide",
    response_format: str = "bundle",
) -> dict[str, Any]:
    """オシロ虎の巻とFAM探索flowをread-onlyで返す。"""

    return get_agent_help(topic=topic, response_format=response_format)  # type: ignore[arg-type]


@mcp.resource(
    "psycho://help/oscilloscope-field-guide",
    mime_type="text/markdown",
)
def oscilloscope_field_guide() -> str:
    """MAD巫女サイエンティストふさもふのAI向けオシロ虎の巻を返す。"""

    result = get_agent_help(response_format="markdown")
    return str(result["data"]["documents"][0]["content"])


@mcp.resource(
    "psycho://help/oscilloscope-fam-flow",
    mime_type="application/json",
)
def oscilloscope_fam_flow() -> str:
    """オシロHELPのFAM.JSON探索profileを返す。"""

    result = get_agent_help(response_format="fam_json")
    content = result["data"]["documents"][0]["content"]
    return json.dumps(content, ensure_ascii=False, indent=2)


def serve_help_mcp() -> None:
    """docs-only MCPをstdioで開始する。実機gateやtransportを開かない。"""

    mcp.run(transport="stdio")
