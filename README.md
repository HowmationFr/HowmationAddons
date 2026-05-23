# Howmation Add-ons

Official [Howmation](https://github.com/HowmationFr) add-on repository for Home Assistant.

## Available add-ons

- [Cerberus SMART Agent](./cerberus_smart_agent) — exposes the host's disk SMART data to the Cerberus HACS integration.
- [Internxt WebDAV](./internxt_webdav) — wraps Internxt CLI as a WebDAV server so Internxt Drive can be used as a backup destination by Home Assistant's core WebDAV integration.

## Adding this repository to Home Assistant

1. Home Assistant → **Settings** → **Add-ons** → **Add-on Store**.
2. **⋯** menu (top right) → **Repositories**.
3. Paste `https://github.com/HowmationFr/HowmationAddons` then **Add**.
4. Howmation add-ons appear at the bottom of the store.

## For developers

Standard layout for a Home Assistant Supervisor add-on repository:

```
HowmationAddons/
├── repository.yaml             # repository metadata
├── README.md                   # this file
├── cerberus_smart_agent/       # one folder per add-on
│   ├── config.yaml             # add-on manifest (slug, version, options…)
│   ├── Dockerfile              # multi-arch image
│   ├── run.sh                  # entrypoint
│   ├── agent.py                # business logic
│   ├── translations/           # i18n strings for the config UI
│   └── README.md               # user-facing documentation
└── internxt_webdav/            # another add-on (same layout, no agent.py)
    ├── config.yaml
    ├── build.yaml
    ├── Dockerfile
    ├── run.sh
    ├── translations/
    └── README.md
```

User-facing strings (options labels, port descriptions) are localized via the HA-native `translations/<lang>.yaml` files per add-on (English + French shipped today). The Supervisor picks the right one based on the user's HA UI language.

Reference: <https://developers.home-assistant.io/docs/add-ons/repository>.
