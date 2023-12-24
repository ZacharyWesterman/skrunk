#!/usr/bin/env bash

function inotif()
{
	inotifywait . -rm -e close_write | while read dir event file
	do
		[ "$(<<<"$dir" grep git)" != "" ] && continue
		path="$dir$file"
		scp "$path" tester:/home/tester/server/"$path"

		if [ "${file##*.}" == 'graphql' ]
		then
			ssh -t tester "sudo systemctl restart server"
		fi
	done
}

function simulate_inotify()
{
	declare -A mods
	for i in $(git status --porcelain | cut -b 3-)
	do
		mods["$i"]=$(date +%s -r "$i")
	done

	while true
	do
		for i in $(git status --porcelain | cut -b 3-)
		do
			mod=$(date +%s -r "$i")
			if [ "$mod" != "${mods["$i"]}" ]
			then
				mods["$i"]="$mod"
				scp "$i" tester:/home/tester/server/"$i"
			fi
		done
	done
}

function sync_files()
{
	if which inotifywait 2>/dev/null
	then
		inotif
	else
		simulate_inotify
	fi
}

ssh -oConnectTimeout=10 -n tester "cd /home/tester/server && git checkout . && git clean -fd && git fetch origin && git checkout $(git branch | grep '*' | cut -b 2-) && git pull" || exit 1
for i in $(git status --porcelain | cut -b 3-)
do
	scp "$i" tester:/home/tester/server/"$i"
done

sync_files

ssh -t tester "
	sudo systemctl restart server
	trap 'sudo systemctl stop server; exit' INT
	journalctl -f -u server
"

kill -TERM -$$
