# Howmation Add-ons for Home Assistant

[![Add repository to my Home Assistant][my-ha-shield]][my-ha]

[![License: MIT][license-shield]][license]
[![Supports amd64][amd64-shield]](#)
[![Supports aarch64][aarch64-shield]](#)
[![Maintained][maintained-shield]][issues]

Custom [Home Assistant](https://www.home-assistant.io) add-ons by [Howmation][howmation].

## Add-ons

### 🗄️ [Internxt WebDAV](./internxt_webdav) &nbsp; ![Version][internxt-version-shield]

Back up Home Assistant to **[Internxt Drive](https://internxt.com)** — private, end-to-end encrypted cloud storage. Runs the official Internxt CLI as a WebDAV server on Home Assistant's internal network, ready to plug into the core WebDAV integration and the built-in backup system.

[📖 Documentation](./internxt_webdav/DOCS.md) · [📝 Changelog](./internxt_webdav/CHANGELOG.md)

## Installation

1. Click the **Add repository** button above, or go to **Settings → Add-ons → Add-on Store**, open the **⋯** menu → **Repositories**, and paste:

   ```text
   https://github.com/HowmationFr/HowmationAddons
   ```

2. The Howmation add-ons appear at the bottom of the store — install, configure, start.

## Repository structure

Standard [Home Assistant add-on repository](https://developers.home-assistant.io/docs/add-ons/repository) layout:

```text
HowmationAddons/
├── repository.yaml           # repository metadata
├── .github/workflows/        # CI: add-on linter + test builds
└── internxt_webdav/          # one folder per add-on
    ├── config.yaml           # add-on manifest (slug, version, options…)
    ├── build.yaml            # pinned upstream base image per arch
    ├── Dockerfile
    ├── run.sh                # startup: options → Internxt CLI
    ├── health_check.sh       # Docker healthcheck wrapper
    ├── DOCS.md               # "Documentation" tab in HA
    ├── CHANGELOG.md
    └── translations/         # config UI strings (EN + FR)
```

User-facing option labels are localized through the HA-native `translations/<lang>.yaml` files; the Supervisor picks the language from your HA UI settings.

## Support

Found a bug or want a feature? [Open an issue][issues].

## Contributing

Pull requests are welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md) for the ground rules (local testing, versioning policy, review process).

## License

[MIT][license] © [Howmation][howmation]

[howmation]: https://github.com/HowmationFr
[issues]: https://github.com/HowmationFr/HowmationAddons/issues
[license]: ./LICENSE
[my-ha]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FHowmationFr%2FHowmationAddons
[my-ha-shield]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[license-shield]: https://img.shields.io/badge/license-MIT-brightgreen.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[maintained-shield]: https://img.shields.io/badge/maintained-yes-brightgreen.svg
[internxt-version-shield]: https://img.shields.io/badge/version-1.0.0-blue.svg
