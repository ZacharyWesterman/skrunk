#!/usr/bin/env bash
server=$1
directory="$(mktemp -d)"

[ "$server" == '' ] && echo 'USAGE: scripts/fetch_and_load_backup.sh [SERVER_ADDRESS]' && exit 1

scripts/create_backup.sh "$server" "$directory"
scripts/upload_backup.sh localhost "$directory"

rm -rf "$directory"
