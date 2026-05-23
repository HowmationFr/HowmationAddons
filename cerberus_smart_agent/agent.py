"""Cerberus SMART Agent.

Small local HTTP server exposing host SMART data via ``smartctl``.
Designed to run as a privileged Home Assistant add-on. No secrets,
no authentication: relies on Docker network isolation, never reaches
outside the Supervisor's internal network.

Endpoints:
- GET /health           -> {"ok": true, "version": "0.1.1"}
- GET /smart/list       -> ``smartctl --scan -j``
- GET /smart/{name}     -> full ``smartctl -a -j /dev/{name}`` output.
  For NVMe, if the controller call (``/dev/nvme0``) doesn't return the
  useful SMART sections, automatically falls back to the namespace
  (``/dev/nvme0n1``). The returned payload always includes ``exit_code``
  and ``stderr`` to make debugging easier.

No mutating commands (--set, --smart, ...) are exposed.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess  # noqa: S404 — controlled call to smartctl only
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

VERSION = "0.1.1"
PORT = int(os.environ.get("CERBERUS_AGENT_PORT", "8099"))
LOG_LEVEL = os.environ.get("CERBERUS_AGENT_LOG_LEVEL", "info").upper()
SMARTCTL = shutil.which("smartctl") or "/usr/sbin/smartctl"
DEVICE_NAME_RE = re.compile(r"^[a-zA-Z0-9_+-]+$")

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("cerberus-agent")


def run_smartctl(args: list[str], timeout: int = 15) -> dict:
    """Run smartctl in JSON mode and return the payload + full status."""
    if not os.path.exists(SMARTCTL):
        return {"ok": False, "error": "smartctl not found", "data": {}, "stderr": "", "exit_code": -1, "cmd": ""}
    cmd = [SMARTCTL, *args, "-j"]
    log.debug("running %s", cmd)
    try:
        result = subprocess.run(  # noqa: S603 — resolved path, controlled args
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (subprocess.SubprocessError, OSError) as err:
        return {
            "ok": False,
            "error": f"{type(err).__name__}: {err}",
            "data": {},
            "stderr": "",
            "exit_code": -1,
            "cmd": " ".join(cmd),
        }
    try:
        payload = json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError as err:
        payload = {}
        log.warning("smartctl JSON decode failed: %s", err)
    return {
        "ok": bool(payload),
        "exit_code": result.returncode,
        "data": payload,
        "stderr": result.stderr[:2000],
        "cmd": " ".join(cmd),
    }


def scan_devices() -> dict:
    return run_smartctl(["--scan"])


def _has_smart_data(payload: dict) -> bool:
    """Heuristic: does the payload contain useful SMART data?"""
    if not isinstance(payload, dict):
        return False
    keys = (
        "smart_status",
        "ata_smart_attributes",
        "nvme_smart_health_information_log",
        "temperature",
        "power_on_time",
        "model_name",
    )
    return any(k in payload for k in keys)


def smart_info(device: str) -> dict:
    """Try multiple smartctl invocations to retrieve SMART data for a device.

    For NVMe: if ``/dev/nvme0`` doesn't return a useful payload, retry with
    ``/dev/nvme0n1`` (namespace 1), which is required on some platforms.
    For SATA: try ``-d auto/sat/scsi`` if auto-detection fails.
    """
    if not DEVICE_NAME_RE.match(device):
        return {"ok": False, "error": "invalid device name"}

    primary = run_smartctl(["-a", f"/dev/{device}"])
    attempts: list[str] = [f"/dev/{device}"]

    if device.startswith("nvme") and not _has_smart_data(primary.get("data", {})):
        # nvme0 -> nvme0n1 (namespace 1) when the detected device has no explicit namespace
        if "n" not in device[4:]:
            ns_device = f"{device}n1"
            attempts.append(f"/dev/{ns_device}")
            ns_result = run_smartctl(["-a", f"/dev/{ns_device}"])
            if _has_smart_data(ns_result.get("data", {})):
                ns_result["fallback_used"] = f"/dev/{ns_device}"
                ns_result["attempts"] = attempts
                return ns_result

    if not _has_smart_data(primary.get("data", {})) and primary.get("exit_code") not in (0, 64):
        for dtype in ("auto", "sat", "scsi"):
            attempts.append(f"/dev/{device} -d {dtype}")
            forced = run_smartctl(["-a", "-d", dtype, f"/dev/{device}"])
            if _has_smart_data(forced.get("data", {})):
                forced["fallback_used"] = f"/dev/{device} -d {dtype}"
                forced["attempts"] = attempts
                return forced

    primary["attempts"] = attempts
    return primary


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        log.info("%s - %s", self.address_string(), format % args)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"

        if path == "/health":
            self._send_json(200, {"ok": True, "version": VERSION, "smartctl": SMARTCTL})
            return
        if path == "/smart/list":
            self._send_json(200, scan_devices())
            return
        if path.startswith("/smart/"):
            device = path[len("/smart/"):]
            self._send_json(200, smart_info(device))
            return

        self._send_json(404, {"ok": False, "error": "not found"})


def main() -> None:
    log.info("Cerberus SMART Agent %s starting on 0.0.0.0:%s", VERSION, PORT)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)  # noqa: S104 — local docker net only
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("agent stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
