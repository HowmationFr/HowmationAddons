# Internxt WebDAV

Runs the official [Internxt CLI](https://github.com/internxt/cli) in WebDAV mode inside a Home Assistant add-on, so **Internxt Drive** can be used as a destination for Home Assistant backups through the core [WebDAV integration](https://www.home-assistant.io/integrations/webdav/).

## How it works

```text
Home Assistant ──WebDAV (HTTP, internal Docker network)──> add-on (Internxt CLI) ──HTTPS──> Internxt Drive
```

Internxt does not publish a hosted WebDAV endpoint — you have to run one yourself with their CLI. This add-on does exactly that, on the same internal Docker network as Home Assistant, with no exposure outside your machine by default.

## Installation

1. **Settings** → **Add-ons** → **Add-on Store**.
2. **⋯** menu (top right) → **Repositories** → add `https://github.com/HowmationFr/HowmationAddons`.
3. Install **Internxt WebDAV**.
4. Fill in the options (below), then start the add-on.
5. Recommended: enable the **Watchdog** toggle on the add-on page (see [Watchdog and self-healing](#watchdog-and-self-healing)).

## Configuration

| Option | Required | Description |
|---|---|---|
| `internxt_email` | yes | Internxt account email. |
| `internxt_password` | yes | Internxt account password. |
| `internxt_otp_secret` | no | Base32 TOTP secret (shown once when you enabled 2FA on your Internxt account). Required only if 2FA is enabled; lets the add-on re-login automatically on every restart. Pasting it with spaces (`xxxx xxxx …`) is fine — they are stripped. |
| `internxt_workspace_id` | no | **Internxt Business / Teams only.** UUID of a team workspace to target instead of your personal drive. Leave empty on a personal account. This is **not** a folder ID — the UUID after `/folder/` in a Drive URL will not work. Find it in the workspace settings on the web UI, or via `internxt workspaces list --json`. |
| `webdav_username` | yes | Username the Home Assistant WebDAV integration will present. Defaults to `homeassistant`. Do **not** reuse your Internxt password here. |
| `webdav_password` | yes | Password the WebDAV server will require. Generate something random and paste the same value into the HA WebDAV integration. |
| `delete_files_permanently` | no | If enabled, files deleted via WebDAV bypass Internxt's trash — recovery is impossible. Leave off unless you have a specific reason. |

The server listens in **plain HTTP** on port 3005. Traffic stays on the Supervisor's internal Docker network, so no TLS is needed internally.

## Connecting the Home Assistant WebDAV integration

After starting the add-on:

1. **Settings** → **Devices & services** → **Add integration** → search **WebDAV**.
2. Fill in:
   - **URL**: `http://aeaf1cfc-internxt-webdav:3005`
     - The `aeaf1cfc-` prefix is a hash of the repository URL. It is **identical for every install** that added the add-on from this repository. If you forked the repo, the prefix changes — find your hostname via `ha addons info internxt_webdav` (field `hostname`).
   - **Username**: value of `webdav_username`.
   - **Password**: value of `webdav_password`.
   - **Verify SSL**: leave as-is — it has no effect over HTTP.
   - **Backup path**: `/` for the Drive root, or a dedicated subfolder (recommended), e.g. `/HomeAssistantBackups`. HA creates it if missing. **This is where you pick the destination folder** — the WebDAV server always exposes the Drive root and HA decides where inside to write.
3. Then **Settings** → **System** → **Backups** → **Add location** → pick the WebDAV agent.

## Networking

By default the add-on is reachable **only** from inside Home Assistant's Docker network (the hostname above). No port is published on your machine or LAN.

If something *outside* Home Assistant needs to reach the WebDAV server (another computer, a NAS sync job…), map the port yourself: add-on page → **Network** section → set a host port for `3005/tcp`. Keep in mind the server speaks plain HTTP with Basic auth — only do this on a network you trust.

## Watchdog and self-healing

The image ships a real Docker healthcheck: it verifies that the CLI session is valid and the WebDAV server reports `online`. Home Assistant uses it to detect the add-on as started (~30–60 s after boot).

Internxt session tokens eventually expire. The healthcheck notices (the add-on turns *unhealthy*), and if the **Watchdog** toggle is enabled, the Supervisor restarts the add-on, which logs in again with your stored credentials — no manual action needed. Without the Watchdog, you'll need to restart the add-on yourself when the session expires.

## Limits

- **40 GB per-file cap** on the Internxt side (see [upstream WEBDAV.md](https://github.com/internxt/cli/blob/main/WEBDAV.md)). A full HA backup can approach this — prefer partial backups if your data is large.
- **Architectures**: `amd64` and `aarch64` only. The upstream image is not published for `armv7` (32-bit Raspberry Pi OS is not supported).
- **Missing WebDAV verbs**: Internxt does not implement `COPY` or `PROPPATCH`. HA's WebDAV integration doesn't need them, but third-party tools might complain.

## Security

- Internal Docker network only by default; the host port mapping is opt-in (see [Networking](#networking)).
- WebDAV authentication is **always enforced** — there is no anonymous mode.
- Your credentials are masked in the UI and stored in the add-on's protected configuration on the host (readable only by root there, and present in full backups). They are **not** encrypted at rest — treat host access and backup files accordingly.
- Storing the TOTP secret trades away part of 2FA's "second factor" property for unattended re-login: anyone who obtains the add-on configuration gets both factors. Use a strong, unique Internxt password.
- While the add-on runs, the credentials also exist in plain form inside the (ephemeral) container filesystem and on the CLI's process arguments at login time — this is inherent to the upstream CLI and confined to the container.
- The container runs under Docker's default confinement and requests no Home Assistant API access.
- No telemetry added by the add-on. Outbound traffic is the Internxt CLI talking to the official Internxt API.

## Known upstream issues

These live in the Internxt CLI itself (pinned to `v1.6.6`); listed here so you don't chase ghosts:

- **Workspace can be silently unset when the session token auto-refreshes.** The CLI's token-refresh path rebuilds the stored credentials without the active workspace. If you use `internxt_workspace_id` (Business), a long-running add-on may flip back to the personal drive after a refresh; restarting the add-on re-selects the workspace. Personal accounts are unaffected.
- **Rate limiting on very large transfers.** Internxt may throttle or temporarily ban aggressive upload bursts; huge full backups are the typical trigger. Partial backups mitigate this.
- **Headless login relies on `login-legacy`**, which upstream has flagged as legacy. The pinned version keeps working; upstream releases are vetted before bumping the pin.

## Troubleshooting

- **Add-on stops immediately** → open the **Log** tab. `configuration error: …` messages tell you exactly which option is missing or malformed.
- **`Invalid credentials`** → check your Internxt email/password. If 2FA is enabled on the account, `internxt_otp_secret` is mandatory.
- **`Workspace not found`** → your `internxt_workspace_id` is probably a folder ID, not a workspace UUID (see [Configuration](#configuration)).
- **HA says "Failed to connect"** → verify the add-on is running, that the username/password in the integration match `webdav_username`/`webdav_password`, and that the URL starts with `http://` (not `https://`).
- **Backup fails mid-flight** → most likely the 40 GB per-file cap. Configure a partial backup or exclude large add-ons.
- **Add-on shows "unhealthy" / restarts by itself** → usually an expired Internxt session being self-healed (see [Watchdog](#watchdog-and-self-healing)). If it loops, check the Log tab for login errors.

## Support

Issues and feature requests: <https://github.com/HowmationFr/HowmationAddons/issues>
