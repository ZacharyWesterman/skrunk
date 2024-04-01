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
for db in weather data notifications inventory
do
	echo "BACKING UP ${db^^}..."
	ssh "$SERVER" "mongodump --db $db --out $tmp"
	rsync -a "$SERVER:$tmp/$db" "." 2>/dev/null || echo 'No data to transfer.'
	ssh "$SERVER" "rm -rf $tmp"
	echo
done

echo "Backed up $SERVER mongo data into $OUTPUT."
