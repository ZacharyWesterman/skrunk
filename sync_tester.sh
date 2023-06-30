#!/usr/bin/env bash

function inotif()
{
	inotifywait . -rm -e close_write | while read dir event file
	do
		[ "$(<<<"$dir" grep git)" != "" ] && continue
		path="$dir$file"
		scp "$path" tester:/home/tester/server/"$path"
	done
}

ssh -oConnectTimeout=10 -n tester "cd /home/tester/server && git clean -fd && git pull" || exit 1
inotif &

ssh -t tester "
	sudo systemctl restart server
	trap 'sudo systemctl stop server; exit' INT
	journalctl -f -u server
"