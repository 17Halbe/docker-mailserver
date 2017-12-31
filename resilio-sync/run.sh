#!/bin/sh
config=""

for file in /tmp/resilio-config/conf.d/*.conf
do
  config=${config}$( cat $file )','
done

config=${config%?}
echo "$( cat /tmp/resilio-config/resilio-master.json )[$config]}" > /tmp/resilio-config/sync.conf
sed -i "s|{DEVICE_NAME}|$DEVICE_NAME|" /tmp/resilio-config/sync.conf

for dir in $( grep "dir" /tmp/resilio-config/conf.d/*.conf | cut -d'"' -s -f4 )
do
	case "$dir" in 
	/*) mkdir -p $dir ;;
	*) mkdir -p /usr/share/resilio-sync/$dir 
	   sed -i "s|$dir|/usr/share/resilio-sync/$dir|" /tmp/resilio-config/sync.conf;;
	esac
	
done

cat /tmp/resilio-config/sync.conf
exec /usr/local/bin/rslsync --config /tmp/resilio-config/sync.conf --nodaemon $*
