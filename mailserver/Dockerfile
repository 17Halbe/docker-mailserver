FROM tvial/docker-mailserver:latest
COPY ./contrib/GnuPG /usr/local/lib/python2.7/dist-packages
COPY ./contrib/register-handler.py /usr/local/bin/register-handler.py
COPY ./contrib/gpg-mailgate.py /usr/local/bin/gpg-mailgate.py
RUN chown nobody:nogroup /usr/local/bin/gpg-mailgate.py
RUN chmod u+x /usr/local/bin/gpg-mailgate.py
RUN chown nobody:nogroup /usr/local/bin/register-handler.py
RUN chmod a+x /usr/local/bin/register-handler.py


#RUN mkdir -p /var/gpgmailgate/smime
#RUN mkdir /var/gpgmailgate/.gnupg
#RUN chown -R nobody:nogroup /var/gpgmailgate/
RUN usermod -d /var/gpgmailgate nobody

RUN echo 'register: |/usr/local/bin/register-handler.py' > /etc/aliases
RUN postalias /etc/aliases

RUN apt-get update -q 
RUN apt-get -y install --no-install-recommends \
  python-m2crypto \
  python-requests \
  python-markdown
