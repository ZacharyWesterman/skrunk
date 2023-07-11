#!/usr/bin/env bash
SERVER=$1
OUTPUT=$2

if [ -z "$SERVER" ] || [ -z "$OUTPUT" ]
then
	>&2 echo "USAGE: $0 [SERVER_ADDRESS] [OUTPUT_DIR]"
	exit 1
fi

rm -rf "$OUTPUT"
mkdir -p "$OUTPUT"
cd "$OUTPUT" || exit 1


tmp="/tmp/$(uuidgen)"
for db in weather data
do
	echo "BACKING UP ${db^^}..."
	while ! ssh "$SERVER" "mongodump --db $db --out $tmp"; do sleep 1; done
	while ! rsync -a "$SERVER:$tmp/$db" "."; do sleep 1; done
	while ! ssh "$SERVER" "rm -rf $tmp"; do sleep 1; done
	echo
done

echo "Backed up $SERVER mongo data into $OUTPUT."