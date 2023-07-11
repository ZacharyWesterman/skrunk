#!/usr/bin/env bash
SERVER=$1
INPUT=$2

if [ -z "$SERVER" ] || [ -z "$INPUT" ]
then
	>&2 echo "USAGE: $0 [SERVER_ADDRESS] [INPUT_DIR]"
	exit 1
fi

[ -d "$INPUT" ] || exit 1

tmp="/tmp/$(uuidgen)"
while ! rsync -a "$INPUT/" "$SERVER:$tmp"; do sleep 1; done
while ! ssh "$SERVER" "mongorestore $tmp"; do sleep 1; done
while ! ssh "$SERVER" "rm -rf $tmp"; do sleep 1; done
