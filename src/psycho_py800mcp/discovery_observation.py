"""有界なBonjour/mDNSおよびDLNA/SSDP観測runbook。"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import ipaddress
import json
import logging
import re
import select
import socket
import struct
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LOGGER = logging.getLogger(__name__)
CONFIRMATION_TOKEN = "I_START_BOUNDED_DISCOVERY_2026-07-17"
BONJOUR_SERVICE_TYPES = (
    "_services._dns-sd._udp",
    "_lxi._tcp",
    "_vxi-11._tcp",
    "_scpi-raw._tcp",
    "_scpi-telnet._tcp",
    "_http._tcp",
)
INSTRUMENT_SERVICE_TYPES = frozenset(BONJOUR_SERVICE_TYPES[1:5])
SSDP_TARGET = ("239.255.255.250", 1900)
SSDP_MAX_DATAGRAMS = 64
SSDP_MAX_DATAGRAM_BYTES = 65_535
IPV4_PATTERN = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")


@dataclass(frozen=True, slots=True)
class DiscoveryRunbook:
    """実行前に固定するnetwork discovery条件。"""

    interface: str
    local_ipv4: str
    bonjour_service_types: tuple[str, ...]
    browse_seconds_per_type: float
    ssdp_listen_seconds: float
    ssdp_target: tuple[str, int]
    ssdp_max_datagrams: int
    permits_tcp_connect: bool = False
    permits_http_fetch: bool = False
    permits_scpi: bool = False
    permits_port_scan: bool = False

    def canonical_json(self) -> str:
        """hash対象の正規JSONを返す。"""

        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    def sha256(self) -> str:
        """runbook hashを返す。"""

        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def build_ssdp_request() -> bytes:
    """固定DLNA/UPnP discovery packetを返す。"""

    return (
        b"M-SEARCH * HTTP/1.1\r\n"
        b"HOST: 239.255.255.250:1900\r\n"
        b'MAN: "ssdp:discover"\r\n'
        b"MX: 1\r\n"
        b"ST: ssdp:all\r\n"
        b"\r\n"
    )


def get_interface_ipv4(interface: str) -> str:
    """macOSの指定interfaceに割り当てられたIPv4を取得する。"""

    result = subprocess.run(
        ["/usr/sbin/ipconfig", "getifaddr", interface],
        check=True,
        capture_output=True,
        text=True,
        timeout=5,
    )
    value = result.stdout.strip()
    address = ipaddress.ip_address(value)
    if not isinstance(address, ipaddress.IPv4Address):
        raise ValueError(f"IPv4ではありません: {value}")
    return value


def validate_runbook(runbook: DiscoveryRunbook) -> None:
    """探索scopeが固定allowlist内であることを検証する。"""

    if runbook.bonjour_service_types != BONJOUR_SERVICE_TYPES:
        raise ValueError("Bonjour service allowlistが固定値と一致しません")
    if not 0.5 <= runbook.browse_seconds_per_type <= 10.0:
        raise ValueError("Bonjour観測時間が許容範囲外です")
    if not 0.5 <= runbook.ssdp_listen_seconds <= 10.0:
        raise ValueError("SSDP観測時間が許容範囲外です")
    if runbook.ssdp_target != SSDP_TARGET:
        raise ValueError("SSDP送信先が固定multicast endpointと一致しません")
    if runbook.ssdp_max_datagrams != SSDP_MAX_DATAGRAMS:
        raise ValueError("SSDP受信上限が固定値と一致しません")
    if any(
        (
            runbook.permits_tcp_connect,
            runbook.permits_http_fetch,
            runbook.permits_scpi,
            runbook.permits_port_scan,
        )
    ):
        raise ValueError("このrunbookは接続・SCPI・port scanを許可しません")


def _decode(value: bytes | None) -> str:
    """BonjourのNUL終端文字列を安全にdecodeする。"""

    return value.decode("utf-8", errors="replace") if value else ""


def browse_bonjour(
    service_type: str,
    interface: str,
    duration_seconds: float,
) -> list[dict[str, Any]]:
    """macOS Bonjour APIで一service typeを指定interface上だけ観測する。"""

    library = ctypes.CDLL("/usr/lib/libSystem.B.dylib")
    service_ref = ctypes.c_void_p()
    interface_index = socket.if_nametoindex(interface)
    records: list[dict[str, Any]] = []
    callback_type = ctypes.CFUNCTYPE(
        None,
        ctypes.c_void_p,
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_int32,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_void_p,
    )

    def callback(
        _service_ref: int,
        flags: int,
        observed_interface_index: int,
        error_code: int,
        service_name: bytes | None,
        registration_type: bytes | None,
        reply_domain: bytes | None,
        _context: int,
    ) -> None:
        records.append(
            {
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "event": "add" if flags & 0x2 else "remove",
                "interface_index": observed_interface_index,
                "error_code": error_code,
                "service_name": _decode(service_name)[:512],
                "registration_type": _decode(registration_type)[:128],
                "reply_domain": _decode(reply_domain)[:256],
            }
        )

    callback_reference = callback_type(callback)
    library.DNSServiceBrowse.argtypes = [
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.c_char_p,
        ctypes.c_char_p,
        callback_type,
        ctypes.c_void_p,
    ]
    library.DNSServiceBrowse.restype = ctypes.c_int32
    library.DNSServiceRefSockFD.argtypes = [ctypes.c_void_p]
    library.DNSServiceRefSockFD.restype = ctypes.c_int
    library.DNSServiceProcessResult.argtypes = [ctypes.c_void_p]
    library.DNSServiceProcessResult.restype = ctypes.c_int32
    library.DNSServiceRefDeallocate.argtypes = [ctypes.c_void_p]

    error = library.DNSServiceBrowse(
        ctypes.byref(service_ref),
        0,
        interface_index,
        service_type.encode("ascii"),
        b"local.",
        callback_reference,
        None,
    )
    if error != 0:
        raise RuntimeError(f"DNSServiceBrowse failed: {error}")

    try:
        descriptor = library.DNSServiceRefSockFD(service_ref)
        deadline = time.monotonic() + duration_seconds
        while time.monotonic() < deadline:
            remaining = max(0.0, deadline - time.monotonic())
            readable, _, _ = select.select([descriptor], [], [], min(0.25, remaining))
            if readable:
                process_error = library.DNSServiceProcessResult(service_ref)
                if process_error != 0:
                    raise RuntimeError(f"DNSServiceProcessResult failed: {process_error}")
    finally:
        library.DNSServiceRefDeallocate(service_ref)
    return records


def parse_ssdp_headers(payload: bytes) -> dict[str, str]:
    """SSDP応答から公開前に選別可能なheaderを抽出する。"""

    text = payload.decode("iso-8859-1", errors="replace")
    lines = text.split("\r\n")
    result = {"status_line": lines[0][:512] if lines else ""}
    for line in lines[1:]:
        if ":" not in line:
            continue
        name, value = line.split(":", 1)
        key = name.strip().lower()
        if key in {"location", "server", "st", "usn", "cache-control", "ext"}:
            result[key] = value.strip()[:2048]
    return result


def observe_ssdp(runbook: DiscoveryRunbook) -> list[dict[str, Any]]:
    """固定SSDP multicastへ一packetだけ送り、有界に応答を保存する。"""

    observations: list[dict[str, Any]] = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as channel:
        channel.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(runbook.local_ipv4))
        channel.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack("b", 1))
        channel.settimeout(0.25)
        channel.sendto(build_ssdp_request(), runbook.ssdp_target)
        deadline = time.monotonic() + runbook.ssdp_listen_seconds
        while time.monotonic() < deadline and len(observations) < runbook.ssdp_max_datagrams:
            try:
                payload, source = channel.recvfrom(SSDP_MAX_DATAGRAM_BYTES)
            except TimeoutError:
                continue
            observations.append(
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "source_ip": source[0],
                    "source_port": source[1],
                    "payload_hex": payload.hex(),
                    "headers": parse_ssdp_headers(payload),
                }
            )
    return observations


def redact_global_ipv4(text: str) -> str:
    """Global IPv4だけを伏せ、private/local IPv4は再現性のため残す。"""

    def replace(match: re.Match[str]) -> str:
        candidate = match.group(0)
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            return candidate
        if not isinstance(address, ipaddress.IPv4Address):
            return candidate
        if address.is_private or address.is_loopback or address.is_link_local or address.is_multicast:
            return candidate
        return "[GLOBAL_IPV4_REDACTED]"

    return IPV4_PATTERN.sub(replace, text)


def execute_runbook(runbook: DiscoveryRunbook, output_directory: Path) -> dict[str, Any]:
    """固定runbookを実行し、Git外directoryへ原本とmanifestを保存する。"""

    validate_runbook(runbook)
    output_directory.mkdir(parents=True, exist_ok=False)
    bonjour_results: dict[str, list[dict[str, Any]]] = {}
    for service_type in runbook.bonjour_service_types:
        LOGGER.info("Bonjour browse: %s", service_type)
        bonjour_results[service_type] = browse_bonjour(
            service_type,
            runbook.interface,
            runbook.browse_seconds_per_type,
        )

    ssdp_results = observe_ssdp(runbook)
    raw = {
        "runbook": asdict(runbook),
        "runbook_sha256": runbook.sha256(),
        "bonjour": bonjour_results,
        "ssdp": ssdp_results,
    }
    raw_path = output_directory / "discovery_raw.json"
    raw_path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    raw_sha256 = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    summary = {
        "runbook_sha256": runbook.sha256(),
        "raw_artifact": str(raw_path),
        "raw_sha256": raw_sha256,
        "bonjour_counts": {key: len(value) for key, value in bonjour_results.items()},
        "ssdp_datagram_count": len(ssdp_results),
        "instrument_service_observed": any(
            bonjour_results.get(service_type) for service_type in INSTRUMENT_SERVICE_TYPES
        ),
        "instrument_io_allowed": False,
        "tcp_connect_performed": False,
        "scpi_performed": False,
        "port_scan_performed": False,
    }
    (output_directory / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    """CLI parserを構築する。"""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--confirmation-token", required=True)
    parser.add_argument("--bonjour-seconds", type=float, default=3.0)
    parser.add_argument("--ssdp-seconds", type=float, default=3.0)
    return parser


def main(arguments: list[str] | None = None) -> int:
    """人間確認token付きで有界discoveryを実行する。"""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    options = build_parser().parse_args(arguments)
    if options.confirmation_token != CONFIRMATION_TOKEN:
        LOGGER.error("confirmation token mismatch; discovery was not started")
        return 3
    local_ipv4 = get_interface_ipv4(options.interface)
    runbook = DiscoveryRunbook(
        interface=options.interface,
        local_ipv4=local_ipv4,
        bonjour_service_types=BONJOUR_SERVICE_TYPES,
        browse_seconds_per_type=options.bonjour_seconds,
        ssdp_listen_seconds=options.ssdp_seconds,
        ssdp_target=SSDP_TARGET,
        ssdp_max_datagrams=SSDP_MAX_DATAGRAMS,
    )
    summary = execute_runbook(runbook, options.output_directory)
    LOGGER.info("summary=%s", redact_global_ipv4(json.dumps(summary, ensure_ascii=False)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
