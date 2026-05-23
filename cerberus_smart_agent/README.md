# Cerberus SMART Agent

Official Cerberus add-on for Home Assistant. Exposes the host's SMART (S.M.A.R.T.) disk data through a local HTTP API consumed by the Cerberus integration.

## Why

Home Assistant runs inside a container with no direct access to block devices. This **privileged, local-only** add-on is the clean way to expose `smartctl` to Cerberus. It **never reaches out** to a third-party service — it's our own component.

## Installation

1. Settings → Add-ons → Add-on Store.
2. Three-dot menu → Repositories → add `https://github.com/HowmationFr/HowmationAddons`.
3. Install "Cerberus SMART Agent".
4. Start the add-on. The Cerberus integration auto-discovers it (Docker hostname `a0d7b954-cerberus-smart-agent`, or `localhost:8099` depending on the network setup).

## Security

- No authentication: the API is reachable only from the Supervisor's internal Docker network (optionally also via `localhost` on the host).
- Read-only: no endpoint mutates SMART configuration.
- No telemetry, no outbound traffic.

## Endpoints

- `GET /health` → `{"ok": true, "version": "0.1.1"}`
- `GET /smart/list` → devices detected via `smartctl --scan`
- `GET /smart/{device}` → full SMART payload (`smartctl -a -j /dev/{device}`)

## Limits

- Works on HAOS and Home Assistant Supervised.
- Container and Core require a different approach (native script, out of scope for this release).
