"""有界network discovery runbookのofflineテスト。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "src"))

from psycho_py800mcp.discovery_observation import (  # noqa: E402
    BONJOUR_SERVICE_TYPES,
    SSDP_MAX_DATAGRAMS,
    SSDP_TARGET,
    DiscoveryRunbook,
    build_ssdp_request,
    parse_ssdp_headers,
    redact_global_ipv4,
    validate_runbook,
)


def valid_runbook() -> DiscoveryRunbook:
    """offlineテスト用の正規runbookを返す。"""

    return DiscoveryRunbook(
        interface="en0",
        local_ipv4="192.168.0.18",
        bonjour_service_types=BONJOUR_SERVICE_TYPES,
        browse_seconds_per_type=3.0,
        ssdp_listen_seconds=3.0,
        ssdp_target=SSDP_TARGET,
        ssdp_max_datagrams=SSDP_MAX_DATAGRAMS,
    )


class DiscoveryObservationTest(unittest.TestCase):
    """network送信を行わずrunbook境界を検証する。"""

    def test_fixed_runbook_is_accepted(self) -> None:
        """固定allowlistと禁止capabilityのrunbookを受理する。"""

        validate_runbook(valid_runbook())

    def test_port_scan_capability_is_rejected(self) -> None:
        """port scanを許可したrunbookを拒否する。"""

        source = valid_runbook()
        invalid = DiscoveryRunbook(
            interface=source.interface,
            local_ipv4=source.local_ipv4,
            bonjour_service_types=source.bonjour_service_types,
            browse_seconds_per_type=source.browse_seconds_per_type,
            ssdp_listen_seconds=source.ssdp_listen_seconds,
            ssdp_target=source.ssdp_target,
            ssdp_max_datagrams=source.ssdp_max_datagrams,
            permits_port_scan=True,
        )
        with self.assertRaises(ValueError):
            validate_runbook(invalid)

    def test_ssdp_packet_is_exact_and_bounded(self) -> None:
        """SSDP packetが固定M-SEARCH一件であることを確認する。"""

        packet = build_ssdp_request()
        self.assertEqual(packet.count(b"M-SEARCH"), 1)
        self.assertIn(b"HOST: 239.255.255.250:1900\r\n", packet)
        self.assertIn(b"MX: 1\r\n", packet)
        self.assertTrue(packet.endswith(b"\r\n\r\n"))

    def test_ssdp_parser_selects_known_headers(self) -> None:
        """SSDP parserがallowlist外headerを捨てる。"""

        parsed = parse_ssdp_headers(
            b"HTTP/1.1 200 OK\r\nLOCATION: http://192.168.0.2/x\r\nX-SECRET: no\r\n\r\n"
        )
        self.assertEqual(parsed["location"], "http://192.168.0.2/x")
        self.assertNotIn("x-secret", parsed)

    def test_only_global_ipv4_is_redacted(self) -> None:
        """local segmentを残しGlobal IPv4だけを伏せる。"""

        redacted = redact_global_ipv4("local=192.168.0.18 global=8.8.8.8 multicast=239.255.255.250")
        self.assertIn("192.168.0.18", redacted)
        self.assertIn("239.255.255.250", redacted)
        self.assertNotIn("8.8.8.8", redacted)
        self.assertIn("[GLOBAL_IPV4_REDACTED]", redacted)


if __name__ == "__main__":
    unittest.main()
