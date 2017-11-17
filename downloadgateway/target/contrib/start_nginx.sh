#!/bin/sh
# Note: I've written this using sh so it works in the busybox container too
echo "installing /etc/nginx/conf.d/download.conf:"

/bin/sed -i 's|<servername_replaced_during_buildtime>|'"$NGINX_SERVERNAMES"'|g' /etc/nginx/conf.d/download.conf
/bin/sed -i 's|<shared_secret_replaced_during_buildtime>|'"$NGINX_SHARED_SECRET"'|g' /etc/nginx/conf.d/download.conf
#/bin/cat /etc/nginx/conf.d/download.conf
# start service in background: 
nginx -g 'daemon off;' 
