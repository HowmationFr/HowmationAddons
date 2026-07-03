# Changelog

## 1.0.0 — 2026-07-03

Initial release. 🎉

- WebDAV server backed by Internxt Drive, powered by the official [Internxt CLI](https://github.com/internxt/cli) (pinned to `v1.6.6`)
- Designed for the Home Assistant core [WebDAV integration](https://www.home-assistant.io/integrations/webdav/) and the built-in backup system
- Mandatory WebDAV authentication — no anonymous mode
- 2FA accounts supported via TOTP secret (masked in the UI), with automatic re-login on every restart
- Internxt Business / Teams workspace support
- Built-in Docker healthcheck: Home Assistant reliably detects the running state, and with the add-on Watchdog toggle enabled, expired sessions self-heal
- Internal-network only by default — no host port mapping unless you opt in
- English and French configuration UI
