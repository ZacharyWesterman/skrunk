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
	echo "WARNING: Inotify utils not found! Simulating behavior."
	echo "         This will consume more resources than Inotify!"

	echo "Building initial list of files..."
	declare -A files
	while read i
	do
		files["$i"]=$(date +%s -r "$i")
	done < <(git status --porcelain | cut -b 3-)

	echo "Watching files..."
	while true
	do
		#Make sure new modified files are watched
		while read file
		do
			if [ "${files["$file"]}" == '' ]
			then
				files["$file"]=NEW
			fi
		done < <(git status --porcelain | cut -b 3-)

		#Check file modify time, and copy up if it's not the same as last mod time
		for file in "${!files[@]}"
		do
			modtime=$(date +%s -r "$file")
			if [ "$modtime" != "${files["$file"]}" ]
			then
				files["$file"]="$modtime"
				scp "$file" tester:/home/tester/server/"$file"

				if [ "${file##*.}" == 'graphql' ]
				then
					ssh -t tester "sudo systemctl restart server"
				fi
			fi
		done
	done
}

function sync_files()
{
	if which inotifywait &>/dev/null
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

sync_files &

ssh -t tester "
	sudo systemctl restart server
	trap 'sudo systemctl stop server; exit' INT
	journalctl -f -u server
"

kill -TERM -$$
