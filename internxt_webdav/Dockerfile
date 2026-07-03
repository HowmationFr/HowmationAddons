ARG BUILD_FROM=internxt/webdav:v1.6.6
FROM $BUILD_FROM

ENV LANG=C.UTF-8

COPY run.sh /run.sh
COPY health_check.sh /health_check.sh
RUN chmod a+x /run.sh /health_check.sh

EXPOSE 3005

# Override the upstream HEALTHCHECK: its script needs $INXT_USER, which only
# exists in run.sh's process env, never in the healthcheck's. /health_check.sh
# rebuilds it from /data/options.json. Each probe spawns two Node CLI
# processes, slow on aarch64 SBCs — hence the generous timeout/start-period
# (failed probes inside start-period don't count, success flips healthy
# immediately).
HEALTHCHECK --interval=30s --timeout=30s --start-period=120s --retries=3 CMD /health_check.sh

ENTRYPOINT ["/run.sh"]
