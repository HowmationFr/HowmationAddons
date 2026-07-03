# Home Assistant Add-on: Internxt WebDAV

[![Version][version-shield]][changelog]
[![Supports amd64][amd64-shield]][docs]
[![Supports aarch64][aarch64-shield]][docs]
[![Powered by Internxt CLI][upstream-shield]][upstream]
[![License: MIT][license-shield]][license]

**Back up Home Assistant to [Internxt Drive](https://internxt.com) — private, zero-knowledge, end-to-end encrypted cloud storage.**

## About

Internxt doesn't offer a hosted WebDAV endpoint, so out of the box it can't be a Home Assistant backup target. This add-on closes that gap: it runs the official [Internxt CLI][upstream] in WebDAV mode on Home Assistant's internal Docker network, and the core [WebDAV integration](https://www.home-assistant.io/integrations/webdav/) does the rest.

```text
Home Assistant ──WebDAV──> this add-on ──HTTPS──> Internxt Drive
```

Your backups never touch the open network: the WebDAV server is reachable only from inside Home Assistant unless you explicitly map the port.

## Highlights

- 🔐 **Auth always on** — WebDAV credentials are mandatory, no anonymous mode
- 🔑 **2FA-friendly** — store your TOTP secret once, the add-on re-logs in on every restart
- 🏢 **Business ready** — optional Internxt Teams workspace targeting
- 🩺 **Self-healing** — a real Docker healthcheck detects expired sessions; with the Watchdog toggle on, the add-on re-logs in by itself
- 🛡️ **Minimal footprint** — no Home Assistant API access requested, internal network only by default
- 📦 **Thin & pinned** — a small wrapper over the official `internxt/webdav` image, pinned to a vetted version (`v1.6.6`)

## Quick start

1. Add this repository to the Add-on Store: `https://github.com/HowmationFr/HowmationAddons`
2. Install **Internxt WebDAV**, fill in your Internxt credentials and a WebDAV username/password, start it.
3. Add the **WebDAV** integration with URL `http://aeaf1cfc-internxt-webdav:3005` and those WebDAV credentials.
4. **Settings → System → Backups → Add location** — done.

Full documentation — options, networking, limits, troubleshooting — lives in the add-on's **Documentation** tab ([DOCS.md][docs]).

## License

[MIT][license] — not affiliated with Internxt. Internxt CLI is a product of [Internxt Universal Technologies SL][upstream].

[changelog]: ./CHANGELOG.md
[docs]: ./DOCS.md
[license]: ../LICENSE
[upstream]: https://github.com/internxt/cli
[version-shield]: https://img.shields.io/badge/version-1.0.0-blue.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[upstream-shield]: https://img.shields.io/badge/internxt%20cli-v1.6.6-0066ff.svg
[license-shield]: https://img.shields.io/badge/license-MIT-brightgreen.svg
