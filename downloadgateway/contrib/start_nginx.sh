#!/bin/sh
echo "installing /etc/nginx/conf.d/download.conf:"
/bin/sed 's|<servername_replaced_during_startup>|'"$VIRTUAL_HOST"'|g' /tmp/conf.d/download.conf > /etc/nginx/conf.d/download.conf
/bin/sed -i 's|<shared_secret_replaced_during_startup>|'"$NGINX_SHARED_SECRET"'|g' /etc/nginx/conf.d/download.conf
/bin/cat /etc/nginx/conf.d/download.conf
# start service in background: 
nginx -g 'daemon off;' 
