# Internxt WebDAV

Home Assistant add-on that runs [Internxt CLI](https://github.com/internxt/cli) in **WebDAV** mode, so **Internxt Drive** can be used as a destination for Home Assistant backups through the core [WebDAV](https://www.home-assistant.io/integrations/webdav/) integration.

This add-on is a thin wrapper around the official `internxt/webdav` image: it exposes the add-on options as the environment variables expected by that image. Internxt reference: <https://internxt.com/en/webdav-rclone>.

## Why

Home Assistant's WebDAV integration expects a network-reachable WebDAV endpoint (URL + username + password). Internxt does not publish such an endpoint as a hosted service — you have to run it yourself via their CLI. With this add-on, the WebDAV server runs on the same Docker network as Home Assistant, with no public exposure, and HA can write its backups there.

## Installation

1. Settings → Add-ons → Add-on Store.
2. Three-dot menu → Repositories → add `https://github.com/HowmationFr/HowmationAddons`.
3. Install "Internxt WebDAV".
4. Fill the options (see below) then start the add-on.
5. In Home Assistant: Settings → Devices & services → Add integration → **WebDAV**. URL `http://aeaf1cfc-internxt-webdav:3005`, username/password = those configured in the add-on.

## Configuration

| Option | Type | Required | Description |
|---|---|---|---|
| `internxt_email` | email | yes | Internxt account email. |
| `internxt_password` | password | yes | Internxt account password. |
| `internxt_otp_secret` | str | no | Base32 TOTP secret (shown once when 2FA is enabled). Allows the add-on to auto-login on restart. |
| `internxt_workspace_id` | str | no | **Internxt Business / Teams only.** ID of a team workspace to target instead of your personal drive. Leave **empty** on a personal account. This is **not** a folder ID (the UUID after `/folder/` in a Drive URL won't work here — you'll get `Workspace not found`). On a Business plan, the ID is in the workspace settings on the web UI, or via `internxt workspaces list --json`. |
| `webdav_username` | str | yes | Username the HA WebDAV integration will present. Defaults to `homeassistant`. **Don't reuse your Internxt password** here. |
| `webdav_password` | password | yes | Password expected by the WebDAV server. Generate something random. |
| `delete_files_permanently` | bool | no | If enabled, files deleted via WebDAV bypass Internxt's trash — recovery is impossible. Leave `false` unless you have a specific reason. |

The server is started in **plain HTTP** on port 3005. Traffic stays on the Supervisor's internal Docker network — no TLS needed internally.

## Wiring it to the HA WebDAV integration

After starting the add-on:

1. Settings → Devices & services → Add integration → search **WebDAV**.
2. Fields:
   - **URL**: `http://aeaf1cfc-internxt-webdav:3005`
     - The `aeaf1cfc-` prefix is a hash of the repository URL (`https://github.com/HowmationFr/HowmationAddons`). It is **identical across all installs** that add the add-on from this official repo.
     - If you forked the repo, the prefix changes. Find it in Settings → Add-ons → Internxt WebDAV → "Documentation" tab (hostname shown there), or via `ha addons info internxt_webdav` from the CLI.
     - Fallback: `http://<your-HAOS-IP>:3005` (e.g. `http://192.168.1.42:3005`) also works since the port is mapped on the host. No hostname to guess, but you'll have to update the IP if it changes.
   - **Username**: value of `webdav_username` (default `homeassistant`).
   - **Password**: value of `webdav_password`.
   - **Verify SSL**: leave checked — no effect over HTTP.
   - **Backup path**: `/` to store at the Drive root, or a dedicated subfolder (recommended) — for example `/HomeAssistantBackups`. HA creates the folder if it doesn't exist. **This is where you choose the destination folder**, not in the add-on: the WebDAV server always exposes the Drive root and HA decides where inside to write.
3. Once the integration is added, Settings → System → Backups → Add location → pick the WebDAV agent.

## Limits

- **40 GB per-file cap** on the Internxt side (see [upstream WEBDAV.md](https://github.com/internxt/cli/blob/main/WEBDAV.md)). A full HA backup can approach this — prefer partial backups if your data is large.
- **Architectures**: `amd64` and `aarch64` only. The upstream `internxt/webdav` image is not published for `armv7` (32-bit Raspberry Pi not supported).
- **Missing WebDAV verbs**: Internxt does not implement `COPY` or `PROPPATCH`. HA's WebDAV integration doesn't need them, but third-party tools might complain.
- **Short session**: the Internxt token can expire. The add-on re-logs in on every container restart — if you see 401s in the logs, restart the add-on.

## Security

- The WebDAV server is exposed **only** on the Supervisor's internal Docker network. The `3005/tcp → 3005` mapping in `config.yaml` also makes the port reachable from the host; if you don't need that (e.g. only HA accesses it via Docker), you can remove the mapping from the add-on's **Network** tab.
- WebDAV authentication is **forced** (`WEBDAV_CUSTOM_AUTH=true`) — no anonymous mode exposed.
- Your Internxt and WebDAV credentials are stored encrypted by the Supervisor (`password` / `email` schema fields).
- No telemetry added by the add-on. Outbound traffic is just Internxt CLI talking to the official Internxt API.

## Troubleshooting

- **Add-on stops immediately**: open the "Log" tab. An error `Error: INXT_USER and INXT_PASSWORD environment variables must be set` means the config isn't filled in or wasn't saved before starting.
- **`Invalid credentials`**: check your Internxt email/password. If 2FA is enabled on your account, `internxt_otp_secret` is mandatory.
- **HA says "Failed to connect"**: verify the add-on is running, that `webdav_username` / `webdav_password` entered in HA match those of the add-on, and that the URL really starts with `http://` (not `https://`).
- **Backup fails mid-flight**: most likely the 40 GB cap. Configure a partial backup or exclude large add-ons.
