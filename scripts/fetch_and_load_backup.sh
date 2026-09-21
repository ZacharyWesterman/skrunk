#!/usr/bin/env bash
server=$1
directory="$(mktemp -d)"

[ "$server" == '' ] && echo 'USAGE: ./fetch_and_load_backup.sh [SERVER_ADDRESS]' && exit 1

./create_backup.sh "$server" "$directory"
./upload_backup.sh localhost "$directory"

rm -rf "$directory"
