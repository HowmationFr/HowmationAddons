## What does this PR do?

<!-- Describe the change and the motivation. Link related issues, e.g. "Fixes #12". -->

## Type of change

- [ ] Bug fix
- [ ] New feature / enhancement
- [ ] Upstream base image bump
- [ ] Documentation only
- [ ] CI / repository tooling

## How was it tested?

<!-- e.g. "docker build + run with a test options.json", "installed as a local add-on on HA OS 16.1 (aarch64), backup to Internxt completed" -->

## Checklist

- [ ] CI is green (lint + amd64/aarch64 test builds)
- [ ] User-visible change: `version` bumped in `internxt_webdav/config.yaml` **and** entry added to `internxt_webdav/CHANGELOG.md` (not needed for docs-only — tell us if you'd rather the maintainer handles the bump)
- [ ] Documentation updated where relevant (`DOCS.md`, `README.md`)
- [ ] No new outbound network calls, binaries, or dependencies without prior discussion in an issue
