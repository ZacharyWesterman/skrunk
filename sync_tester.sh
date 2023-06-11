#!/usr/bin/env bash

inotifywait . -rm -e close_write | while read dir event file
do
	[ "$(<<<"$dir" grep git)" != "" ] && continue
	path="$dir$file"
	scp "$path" graphql:/home/ubuntu/server/"$path"
done