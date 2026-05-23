#!/bin/sh
# Internxt WebDAV — wrapper de démarrage pour Home Assistant.
# Lit /data/options.json (fourni par le Supervisor), exporte les variables
# attendues par l'image upstream internxt/webdav, puis exec son entrypoint.

set -eu

CONFIG_PATH="/data/options.json"

if [ ! -f "$CONFIG_PATH" ]; then
  echo "[internxt-webdav] /data/options.json introuvable, abandon." >&2
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
  echo "[internxt-webdav] erreur de configuration : internxt_email et internxt_password sont obligatoires." >&2
  exit 1
fi
if [ -z "$WEBDAV_USERNAME" ] || [ -z "$WEBDAV_PASSWORD" ]; then
  echo "[internxt-webdav] erreur de configuration : webdav_username et webdav_password sont obligatoires." >&2
  exit 1
fi

export INXT_USER INXT_PASSWORD INXT_OTPTOKEN INXT_WORKSPACE_ID
export WEBDAV_PORT=3005
export WEBDAV_PROTOCOL=http
export WEBDAV_CUSTOM_AUTH=true
export WEBDAV_USERNAME WEBDAV_PASSWORD WEBDAV_DELETE_FILES_PERMANENTLY

echo "[internxt-webdav] démarrage (compte=${INXT_USER}, port=${WEBDAV_PORT}, protocole=${WEBDAV_PROTOCOL}, user webdav=${WEBDAV_USERNAME})"

exec /app/docker/entrypoint.sh
