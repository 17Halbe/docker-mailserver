#!/bin/sh

new_sync()
{
	key=$( sudo docker exec -ti sync rslsync --generate-secret )
	echo "Enter the relative(will live its lonely life in /usr/share/resilio-sync/) or absolute folder path for the sync:"
	read sync_path
	case "$sync_path" in 
		/*) break;;
		*) sync_path="/usr/share/resilio-sync/$sync_path" ;;
	esac	
	while true; do
		echo "Enter a Name for the Sync:"
		read sync_name
		ls ./config/conf.d/$sync_name.conf > /dev/null 2>&1
		case "$?" in 
		2)  
		  echo "{
  \"secret\" : \"${key%?}\", // required field - use --generate-secret in command line to create new secret                                                     
  \"dir\" : \"$sync_path\", // * required field  ----> Relative Paths will be put in /usr/share/resilio-sync/ <----
  \"search_lan\" : false,                                                                                     
  \"use_sync_trash\" : true, // enable SyncArchive to store files deleted on remote devices                                             
  \"overwrite_changes\" : false // restore modified files to original version, ONLY for Read-Only folders 
}" > ./config/conf.d/$sync_name.conf
		  echo "File created successfully!"; break
		;;
		*) echo "File exists. Please use a different name!" 
		;;
		esac 
	done
	
	echo "The new secret is: $key"
}

setup_sync()
{
	echo "Enter the secret key:"
	read key
	echo "Enter the relative(will live its lonely life in /usr/share/resilio-sync/) or absolute folder path for the sync:"
	read sync_path
	case "$sync_path" in 
		/*) break;;
		*) sync_path="/usr/share/resilio-sync/$sync_path" ;;
	esac	
	while true; do
		echo "Enter a Name for the Sync:"
		read sync_name
		ls ./config/conf.d/$sync_name.conf > /dev/null 2>&1
		case "$?" in 
		2)  
		  echo "{
  \"secret\" : \"${key%?}\", // required field - use --generate-secret in command line to create new secret                                                     
  \"dir\" : \"$sync_path\", // * required field  ----> Relative Paths will be put in /usr/share/resilio-sync/ <----
  \"search_lan\" : false,                                                                                     
  \"use_sync_trash\" : true, // enable SyncArchive to store files deleted on remote devices                                             
  \"overwrite_changes\" : false // restore modified files to original version, ONLY for Read-Only folders 
}" > ./config/conf.d/$sync_name.conf
		  echo "File created successfully!"; break
		;;
		*) echo "File exists. Please use a different name!" 
		;;
		esac 
	done
}
#get_key()
#{

#}

choice=""

while [ "$choice" != "q" ]
do
        echo
        echo "Please make a selection!"
        echo "1) Generate new Sync-folder"
     	echo "2) Setup new sync with a known secret"
 #       echo "3) Get Read-only key of Volume"
        echo "q) Quit"
        echo

        read choice

        case $choice in
            '1') new_sync ;;
            '2') setup_sync ;;
			'3') get_key ;;
            'q') echo "quiting!" ;;
            *)   echo "menu item is not available; try again!" ;;
        esac
done

