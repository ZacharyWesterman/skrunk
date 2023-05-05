#!/usr/bin/env bash
SERVER=$1
OUTPUT=$2

if [ -z "$SERVER" ] || [ -z "$OUTPUT" ]
then
	>&2 echo "USAGE: $0 [SERVER_ADDRESS] [OUTPUT_DIR]"
	exit 1
fi

declare -A MONGO_NAMES
MONGO_NAMES[data]="blob books bug_reports user_sessions users"
MONGO_NAMES[weather]="alert_history log users"

mkdir -p "$OUTPUT"
cd "$OUTPUT" || exit 1

for db in "${!MONGO_NAMES[@]}"
do
	for coll in ${MONGO_NAMES[$db]}
	do
		echo "$db : $coll"
		ssh "$SERVER" "mongoexport --db \"$db\" --collection \"$coll\"" > "${db}_${coll}".json &
	done
done

wait