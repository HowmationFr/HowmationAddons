#!/bin/sh
# Internxt WebDAV — Home Assistant startup script.
#
# Reads /data/options.json (mounted by the Supervisor) and drives the pinned
# Internxt CLI directly with properly quoted arguments. The upstream docker
# entrypoint (/app/docker/entrypoint.sh) expands its argument strings
# unquoted, which word-splits any credential containing whitespace — so it
# is bypassed on purpose. The sequence below mirrors upstream v1.6.6.

set -eu

CONFIG_PATH="/data/options.json"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "[internxt-webdav] /data/options.json not found, aborting." >&2
  exit 1
fi

opt() {
  jq -r --arg key "$1" '.[$key] // ""' "$CONFIG_PATH"
}

opt_bool() {
  jq -r --arg key "$1" '.[$key] // false | tostring' "$CONFIG_PATH"
}

INXT_USER=$(opt internxt_email)
INXT_PASSWORD=$(opt internxt_password)
# TOTP secrets are conventionally displayed in space-separated groups of 4;
# whitespace is never part of the Base32 payload, so strip it.
INXT_OTPTOKEN=$(opt internxt_otp_secret | tr -d '[:space:]')
INXT_WORKSPACE_ID=$(opt internxt_workspace_id)
WEBDAV_USERNAME=$(opt webdav_username)
WEBDAV_PASSWORD=$(opt webdav_password)
DELETE_FILES_PERMANENTLY=$(opt_bool delete_files_permanently)

if [ -z "$INXT_USER" ] || [ -z "$INXT_PASSWORD" ]; then
  echo "[internxt-webdav] configuration error: internxt_email and internxt_password are required." >&2
  exit 1
fi
if [ -z "$WEBDAV_USERNAME" ] || [ -z "$WEBDAV_PASSWORD" ]; then
  echo "[internxt-webdav] configuration error: webdav_username and webdav_password are required." >&2
  exit 1
fi
if [ -n "$INXT_WORKSPACE_ID" ]; then
  if ! printf '%s' "$INXT_WORKSPACE_ID" | grep -Eq '^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'; then
    echo "[internxt-webdav] configuration error: internxt_workspace_id must be a workspace UUID (run 'internxt workspaces list'). A folder ID from a Drive URL will not work." >&2
    exit 1
  fi
fi

echo "[internxt-webdav] starting (account=${INXT_USER}, port=3005, protocol=http, webdav user=${WEBDAV_USERNAME})"

echo "[internxt-webdav] logging in to ${INXT_USER}..."
if [ -n "$INXT_OTPTOKEN" ]; then
  internxt login-legacy -x -e="$INXT_USER" -p="$INXT_PASSWORD" -t="$INXT_OTPTOKEN"
else
  internxt login-legacy -x -e="$INXT_USER" -p="$INXT_PASSWORD"
fi

if [ -n "$INXT_WORKSPACE_ID" ]; then
  echo "[internxt-webdav] switching to workspace ${INXT_WORKSPACE_ID}"
  internxt workspaces use -x -i="$INXT_WORKSPACE_ID"
fi

if [ "$DELETE_FILES_PERMANENTLY" = "true" ]; then
  echo "[internxt-webdav] WARNING: permanent file deletion is enabled — deleted files will NOT be recoverable."
  internxt webdav-config -l=0.0.0.0 -p=3005 -h --customAuth -u="$WEBDAV_USERNAME" -w="$WEBDAV_PASSWORD" -d
else
  internxt webdav-config -l=0.0.0.0 -p=3005 -h --customAuth -u="$WEBDAV_USERNAME" -w="$WEBDAV_PASSWORD"
fi

internxt webdav enable

LOG_DIR=/root/.internxt-cli/logs
LOG_FILE="$LOG_DIR/internxt-webdav-combined.log"
mkdir -p "$LOG_DIR"
touch "$LOG_FILE"
# exec so SIGTERM reaches tail directly and the container stops promptly.
exec tail -f "$LOG_FILE"
