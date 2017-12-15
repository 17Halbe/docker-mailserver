#!/bin/sh
# Note: I've written this using sh so it works in the busybox container too
echo "installing /etc/nginx/conf.d/download.conf:"

/bin/sed 's|<servername_replaced_during_buildtime>|downloads.'"$DOMAINNAME}"'|g' /tmp/conf.d/download.conf > /etc/nginx/conf.d/download.conf
/bin/sed 's|<shared_secret_replaced_during_buildtime>|'"$NGINX_SHARED_SECRET"'|g' /etc/nginx/conf.d/download.conf
#/bin/cat /etc/nginx/conf.d/download.conf
# start service in background: 
nginx -g 'daemon off;' 
