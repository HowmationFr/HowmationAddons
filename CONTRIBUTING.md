# Contributing

Thanks for your interest in improving the Howmation add-ons! Contributions are welcome — bug reports, documentation fixes, and code changes alike.

## Before you start

- **Open an issue first** for anything non-trivial (new option, behavior change, upstream bump). It avoids wasted work if the change doesn't fit the add-on's scope.
- These add-ons run **as privileged containers in people's homes and hold their credentials**. Changes that add outbound network calls, binaries, or dependencies will not be merged without prior discussion in an issue — please don't take a request for justification personally, it applies to everyone.

## Proposing a change

1. Fork the repository and create a branch from `main`.
2. Make your change. Keep it focused — one topic per pull request.
3. Test it locally (see below).
4. Open a pull request against `main` and fill in the template. CI (add-on linter + amd64/aarch64 test builds) must be green.

Pull requests are squash-merged after review.

## Testing locally

You need Docker. From the repository root:

```bash
# Build the add-on image (BUILD_FROM must match build.yaml)
docker build \
  --build-arg BUILD_FROM=$(sed -n 's/^  amd64:[[:space:]]*//p' internxt_webdav/build.yaml) \
  -t internxt-webdav-dev internxt_webdav/

# Run it with a test configuration (the Supervisor normally provides this file)
cat > /tmp/options.json <<'EOF'
{
  "internxt_email": "you@example.com",
  "internxt_password": "your-password",
  "webdav_username": "homeassistant",
  "webdav_password": "some-random-string",
  "delete_files_permanently": false
}
EOF
docker run --rm -p 3005:3005 -v /tmp/options.json:/data/options.json:ro internxt-webdav-dev
```

The definitive test is running it as a [local add-on](https://developers.home-assistant.io/docs/add-ons/testing) on a real Home Assistant installation.

Shell scripts must keep **LF line endings** (`.gitattributes` enforces this — don't fight it, a CRLF shebang kills the container at startup).

## Versioning and releases

Users' Home Assistant installations build straight from `main`, so **merging is shipping**:

- A **user-visible change** (behavior, options, base image bump) must include a `version` bump in `internxt_webdav/config.yaml` **and** a new entry in `internxt_webdav/CHANGELOG.md`. If in doubt, the maintainer will handle the bump at merge time — say so in the PR.
- **Docs-only** changes don't need a version bump.
- The maintainer tags releases (`vX.Y.Z`) after merge.

## Reporting security issues

Please **do not** open a public issue for security vulnerabilities. Use GitHub's private vulnerability reporting ("Security" tab → "Report a vulnerability") instead.
