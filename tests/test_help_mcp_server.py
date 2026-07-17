"""AI HELP専用FastMCPサーバーのin-memory protocolテスト。"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))


class HelpMcpServerTest(unittest.IsolatedAsyncioTestCase):
    """FastMCPの実protocol面をnetworkなしで検証する。"""

    async def test_help_tool_and_resource_are_read_only(self) -> None:
        """toolとresourceがHELPを返し実機権限を持たない。"""

        from fastmcp import Client

        from psycho_py800mcp.help_mcp_server import mcp

        async with Client(mcp) as client:
            tools = await client.list_tools()
            resources = await client.list_resources()
            tool_result = await client.call_tool(
                "get_help",
                {"topic": "oscilloscope_field_guide", "response_format": "bundle"},
            )
            resource_result = await client.read_resource(
                "psycho://help/oscilloscope-fam-flow"
            )

        self.assertIn("get_help", {tool.name for tool in tools})
        self.assertIn(
            "psycho://help/oscilloscope-field-guide",
            {str(resource.uri) for resource in resources},
        )
        self.assertFalse(tool_result.data["data"]["instrument_io_allowed"])
        flow = json.loads(resource_result[0].text)
        self.assertTrue(flow["execution_bounds"]["unknown_is_not_pass"])


if __name__ == "__main__":
    unittest.main()
