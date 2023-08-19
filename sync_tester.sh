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

ssh -oConnectTimeout=10 -n tester "cd /home/tester/server && git checkout . && git clean -fd && git fetch origin && git checkout $(git branch | grep '*' | cut -b 2-) && git pull" || exit 1
for i in $(git status --porcelain | cut -b 3-)
do
	scp "$i" tester:/home/tester/server/"$i"
done

inotif &

ssh -t tester "
	sudo systemctl restart server
	trap 'sudo systemctl stop server; exit' INT
	journalctl -f -u server
"

kill -TERM -$$