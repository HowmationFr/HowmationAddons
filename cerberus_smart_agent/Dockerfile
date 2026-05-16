ARG BUILD_FROM
FROM $BUILD_FROM

ENV LANG=C.UTF-8

RUN apk add --no-cache \
        smartmontools \
        nvme-cli \
        python3 \
        py3-pip \
    && rm -rf /var/cache/apk/*

COPY agent.py /opt/cerberus/agent.py
COPY run.sh /run.sh
RUN chmod a+x /run.sh

EXPOSE 8099
CMD [ "/run.sh" ]
