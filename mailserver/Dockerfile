FROM tvial/docker-mailserver:latest
COPY ./contrib/GnuPG /usr/local/lib/python2.7/dist-packages

#RUN mkdir -p /var/gpgmailgate/smime
#RUN mkdir /var/gpgmailgate/.gnupg
#RUN chown -R nobody:nogroup /var/gpgmailgate/

RUN usermod -d /var/gpgmailgate nobody

RUN apt-get update -q 
RUN apt-get -y install --no-install-recommends \
  python-m2crypto \
  python-requests \
  python-markdown
