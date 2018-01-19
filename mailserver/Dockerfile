FROM tvial/docker-mailserver:latest
RUN mkdir /usr/local/lib/python2.7/dist-packages/GnuPG
COPY ./contrib/GnuPG /usr/local/lib/python2.7/dist-packages/GnuPG

#RUN mkdir -p /var/gpgmailgate/smime
#RUN mkdir /var/gpgmailgate/.gnupg
#RUN chown -R nobody:nogroup /var/gpgmailgate/
RUN mkdir -p /var/attachments/.futuremails
RUN chown -R docker:docker /var/attachments

RUN usermod -d /var/gpgmailgate nobody

RUN apt-get update -q 
RUN apt-get -y install --no-install-recommends \
  python-m2crypto \
  python-requests \
  python-markdown

