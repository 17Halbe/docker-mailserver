FROM alpine:latest
MAINTAINER Alex <alex-resilio-sync@gar-nich.net>

ENV RESILIO_VERSION="stable" \
    DUMB_INIT_VERSION="1.2.0" \
    GLIBC_VERSION="2.23-r3"

# Install packages
RUN echo " ---> Upgrading OS and installing dependencies" \
  && TMP_APK='curl tar ca-certificates' \
  && apk --update upgrade \
  && apk add $TMP_APK \
  && apk add --update openssl
  # glibc
RUN echo " ---> Installing glibc (${GLIBC_VERSION})" \
  && >&2 echo "glibc-${GLIBC_VERSION}.apk" \
  && curl -#LOS https://github.com/sgerrand/alpine-pkg-glibc/releases/download/${GLIBC_VERSION}/glibc-${GLIBC_VERSION}.apk \
  && >&2 echo "sgerrand.rsa.pub" \
  && curl -#LS -o /etc/apk/keys/sgerrand.rsa.pub https://github.com/sgerrand/alpine-pkg-glibc/releases/download/${GLIBC_VERSION}/sgerrand.rsa.pub \
  && apk add glibc-${GLIBC_VERSION}.apk \
  && rm /etc/apk/keys/sgerrand.rsa.pub glibc-${GLIBC_VERSION}.apk 
  # resilio-sync
RUN echo " ---> Installing resilio-sync (${RESILIO_VERSION})" 
RUN curl -#LS https://download-cdn.resilio.com/${RESILIO_VERSION}/linux-glibc-x64/resilio-sync_glibc23_x64.tar.gz | tar xzf - -C /usr/local/bin rslsync 
RUN chmod +x /usr/local/bin/rslsync 
  # cleanup tmp
RUN echo " ---> Cleaning" \
  && apk del --purge $TMP_APK \
  && rm -rf /var/cache/apk/* \
  && rm -rf /tmp/* 

RUN wget -O /usr/local/bin/dumb-init https://github.com/Yelp/dumb-init/releases/download/v${DUMB_INIT_VERSION}/dumb-init_${DUMB_INIT_VERSION}_amd64
RUN chmod +x /usr/local/bin/dumb-init

RUN mkdir -p /var/lib/resilio/storage-config

COPY run.sh /usr/local/bin
RUN chmod +x /usr/local/bin/run.sh

RUN  ls -al /var/lib/resilio/storage-config > /dev/stdout \
  && echo " ---> Done installing"

EXPOSE 55555 3838

VOLUME ./config:/tmp/resilio-config

ENTRYPOINT ["/usr/local/bin/dumb-init", "/usr/local/bin/run.sh"]
#CMD ["--log /dev/stdout"]
