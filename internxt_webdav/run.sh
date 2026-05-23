#!/bin/sh
# Internxt WebDAV — Home Assistant startup wrapper.
# Reads /data/options.json (mounted by the Supervisor), exports the env vars
# expected by the upstream internxt/webdav image, then execs its entrypoint.

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
INXT_OTPTOKEN=$(opt internxt_otp_secret)
INXT_WORKSPACE_ID=$(opt internxt_workspace_id)
WEBDAV_USERNAME=$(opt webdav_username)
WEBDAV_PASSWORD=$(opt webdav_password)
WEBDAV_DELETE_FILES_PERMANENTLY=$(opt_bool delete_files_permanently)

if [ -z "$INXT_USER" ] || [ -z "$INXT_PASSWORD" ]; then
  echo "[internxt-webdav] configuration error: internxt_email and internxt_password are required." >&2
  exit 1
fi
if [ -z "$WEBDAV_USERNAME" ] || [ -z "$WEBDAV_PASSWORD" ]; then
  echo "[internxt-webdav] configuration error: webdav_username and webdav_password are required." >&2
  exit 1
fi

export INXT_USER INXT_PASSWORD INXT_OTPTOKEN INXT_WORKSPACE_ID
export WEBDAV_PORT=3005
export WEBDAV_PROTOCOL=http
export WEBDAV_CUSTOM_AUTH=true
export WEBDAV_USERNAME WEBDAV_PASSWORD WEBDAV_DELETE_FILES_PERMANENTLY

echo "[internxt-webdav] starting (account=${INXT_USER}, port=${WEBDAV_PORT}, protocol=${WEBDAV_PROTOCOL}, webdav user=${WEBDAV_USERNAME})"

exec /app/docker/entrypoint.sh
