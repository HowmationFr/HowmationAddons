#!/usr/bin/env sh
# Cerberus SMART Agent — startup wrapper.

set -eu

CONFIG_PATH="/data/options.json"

if [ -f "$CONFIG_PATH" ]; then
  LOG_LEVEL=$(python3 -c "import json; print(json.load(open('$CONFIG_PATH')).get('log_level', 'info'))")
else
  LOG_LEVEL="info"
fi

export CERBERUS_AGENT_LOG_LEVEL="$LOG_LEVEL"
export CERBERUS_AGENT_PORT="${CERBERUS_AGENT_PORT:-8099}"

echo "[cerberus-agent] starting on port ${CERBERUS_AGENT_PORT} (log level: ${LOG_LEVEL})"
exec python3 -u /opt/cerberus/agent.py
