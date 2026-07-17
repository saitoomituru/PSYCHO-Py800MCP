"""接続AIへproject-local HELP文書を返すread-only API。"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal


HelpTopic = Literal["oscilloscope_field_guide", "oscilloscope_fam_flow"]
HelpFormat = Literal["markdown", "fam_json", "bundle"]

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
AGENT_DOCS_ROOT = REPOSITORY_ROOT / "docs" / "agi"
FIELD_GUIDE_PATH = AGENT_DOCS_ROOT / "MAD巫女サイエンティストふさもふのAIのためのオシロ虎の巻.proton.md"
FAM_FLOW_PATH = AGENT_DOCS_ROOT / "oscilloscope-help-flow.fam.json"


@dataclass(frozen=True, slots=True)
class HelpDocument:
    """AI向けHELP文書とprovenanceを表す。"""

    topic: str
    media_type: str
    relative_path: str
    sha256: str
    content: str | dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """JSON化可能な辞書へ変換する。"""

        return asdict(self)


_TOPICS: dict[str, tuple[Path, str]] = {
    "oscilloscope_field_guide": (FIELD_GUIDE_PATH, "text/markdown"),
    "oscilloscope_fam_flow": (FAM_FLOW_PATH, "application/json"),
}


def _timestamp() -> str:
    """UTCのISO 8601 timestampを返す。"""

    return datetime.now(UTC).isoformat()


def _load_topic(topic: str) -> HelpDocument:
    """allowlist済みtopicを読み込む。任意pathは受け付けない。"""

    try:
        path, media_type = _TOPICS[topic]
    except KeyError as exc:
        raise ValueError(f"unknown help topic: {topic}") from exc

    raw = path.read_bytes()
    text = raw.decode("utf-8")
    content: str | dict[str, Any]
    if media_type == "application/json":
        content = json.loads(text)
    else:
        content = text

    return HelpDocument(
        topic=topic,
        media_type=media_type,
        relative_path=str(path.relative_to(REPOSITORY_ROOT)),
        sha256=hashlib.sha256(raw).hexdigest(),
        content=content,
    )


def list_agent_help_topics() -> dict[str, Any]:
    """公開可能なAI HELP topic一覧を返す。"""

    return {
        "status": "ok",
        "timestamp": _timestamp(),
        "data": {
            "topics": [
                {
                    "topic": topic,
                    "media_type": media_type,
                    "relative_path": str(path.relative_to(REPOSITORY_ROOT)),
                }
                for topic, (path, media_type) in _TOPICS.items()
            ],
            "read_only": True,
            "instrument_io_allowed": False,
        },
    }


def get_agent_help(
    topic: HelpTopic = "oscilloscope_field_guide",
    response_format: HelpFormat = "bundle",
) -> dict[str, Any]:
    """接続AIへHELP本文、FAM flow、または両方を返す。"""

    if topic not in _TOPICS:
        raise ValueError(f"unknown help topic: {topic}")

    if response_format == "markdown":
        documents = [_load_topic("oscilloscope_field_guide")]
    elif response_format == "fam_json":
        documents = [_load_topic("oscilloscope_fam_flow")]
    elif response_format == "bundle":
        if topic == "oscilloscope_fam_flow":
            documents = [_load_topic("oscilloscope_fam_flow")]
        else:
            documents = [
                _load_topic("oscilloscope_field_guide"),
                _load_topic("oscilloscope_fam_flow"),
            ]
    else:
        raise ValueError(f"unknown help format: {response_format}")

    return {
        "status": "ok",
        "timestamp": _timestamp(),
        "data": {
            "documents": [document.to_dict() for document in documents],
            "read_only": True,
            "instrument_io_allowed": False,
            "authorization_effect": "none",
            "fam_lineage": "FAMoverMCP_toy_model",
        },
    }
