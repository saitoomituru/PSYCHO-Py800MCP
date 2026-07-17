"""接続AI向けHELP APIのテスト。"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from psycho_py800mcp.help_api import (  # noqa: E402
    get_agent_help,
    list_agent_help_topics,
)
from psycho_py800mcp.main import main  # noqa: E402


class AgentHelpApiTest(unittest.TestCase):
    """HELP APIがread-only allowlistとして動作することを確認する。"""

    def test_bundle_contains_field_guide_and_fam_flow(self) -> None:
        """bundleがMarkdownとFAM JSONの両方を返す。"""

        result = get_agent_help()
        documents = result["data"]["documents"]

        self.assertEqual(result["status"], "ok")
        self.assertEqual(len(documents), 2)
        self.assertFalse(result["data"]["instrument_io_allowed"])
        self.assertEqual(result["data"]["authorization_effect"], "none")
        self.assertIn("オシロ虎の巻", documents[0]["content"])
        self.assertEqual(documents[1]["content"]["root"]["status"], "validated_in_context")

    def test_fam_flow_separates_astral_and_elemental_errors(self) -> None:
        """人間非承認とmachine failureが別nodeへrouteされる。"""

        result = get_agent_help(response_format="fam_json")
        flow = result["data"]["documents"][0]["content"]
        children = {child["node_id"]: child for child in flow["root"]["children"]}

        self.assertEqual(
            children["fam:psycho:help:astral-rejection"]["λ"]["status"],
            "REJECTED_FOR_REPLAN",
        )
        self.assertEqual(
            children["fam:psycho:help:elemental-runtime"]["λ"]["status"],
            "ELEMENTAL_RUNTIME_FAILURE",
        )

    def test_unknown_topic_does_not_open_arbitrary_path(self) -> None:
        """任意path風のtopicを拒否する。"""

        with self.assertRaises(ValueError):
            get_agent_help(topic="../../AGENTS.md")  # type: ignore[arg-type]

    def test_topic_list_has_no_instrument_authority(self) -> None:
        """topic一覧が実機権限を宣言しない。"""

        result = list_agent_help_topics()
        self.assertTrue(result["data"]["read_only"])
        self.assertFalse(result["data"]["instrument_io_allowed"])

    def test_cli_can_return_fam_json(self) -> None:
        """CLI HELPがFAM JSONを返せる。"""

        from contextlib import redirect_stdout
        from io import StringIO

        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(["help", "--format", "fam_json"])

        payload = json.loads(output.getvalue())
        self.assertEqual(exit_code, 0)
        self.assertEqual(payload["status"], "ok")


if __name__ == "__main__":
    unittest.main()
