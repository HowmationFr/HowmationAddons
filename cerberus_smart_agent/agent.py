"""Cerberus SMART Agent.

Petit serveur HTTP local exposant les données SMART du host via ``smartctl``.
Conçu pour être lancé comme add-on Home Assistant privilégié. Aucun secret,
aucune authentification : isolation réseau Docker, ne sort jamais du réseau
interne du Supervisor.

Endpoints :
- GET /health           -> {"ok": true, "version": "0.1.0"}
- GET /smart/list       -> {"devices": [...]} via `smartctl --scan -j`
- GET /smart/{name}     -> sortie complète `smartctl -a -j /dev/{name}`

Aucune commande de modification (`--set`, `--smart`, etc.) n'est exposée.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess  # noqa: S404 — appel contrôlé à smartctl uniquement
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

VERSION = "0.1.0"
PORT = int(os.environ.get("CERBERUS_AGENT_PORT", "8099"))
LOG_LEVEL = os.environ.get("CERBERUS_AGENT_LOG_LEVEL", "info").upper()
SMARTCTL = shutil.which("smartctl") or "/usr/sbin/smartctl"
DEVICE_NAME_RE = re.compile(r"^[a-zA-Z0-9_+-]+$")

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("cerberus-agent")


def run_smartctl(args: list[str], timeout: int = 10) -> dict:
    """Exécute smartctl en mode JSON et retourne le payload + status."""
    if not os.path.exists(SMARTCTL):
        return {"ok": False, "error": "smartctl not found", "stdout": "", "stderr": ""}
    cmd = [SMARTCTL, *args, "-j"]
    log.debug("running %s", cmd)
    try:
        result = subprocess.run(  # noqa: S603 — chemin résolu, args contrôlés
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except (subprocess.SubprocessError, OSError) as err:
        return {"ok": False, "error": f"{type(err).__name__}: {err}"}
    payload: dict = {}
    try:
        payload = json.loads(result.stdout) if result.stdout else {}
    except json.JSONDecodeError:
        payload = {}
    return {
        "ok": result.returncode in (0, 64),  # 64 = warnings, OK
        "exit_code": result.returncode,
        "data": payload,
        "stderr": result.stderr[:2000],
    }


def scan_devices() -> dict:
    return run_smartctl(["--scan"])


def smart_info(device: str) -> dict:
    if not DEVICE_NAME_RE.match(device):
        return {"ok": False, "error": "invalid device name"}
    return run_smartctl(["-a", f"/dev/{device}"])


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
