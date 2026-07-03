#!/bin/sh
# Docker healthchecks don't inherit env vars exported by run.sh at runtime
# (they only get the container's static config env), so the upstream check
# always fails in the add-on: it compares `internxt whoami` against an empty
# $INXT_USER. Re-derive INXT_USER from the add-on options, then run the
# upstream check unchanged.
INXT_USER=$(jq -r '.internxt_email // ""' /data/options.json)
export INXT_USER
exec /app/docker/health_check.sh
