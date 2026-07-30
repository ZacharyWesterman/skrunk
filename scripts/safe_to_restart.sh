#!/usr/bin/env bash

# This script checks if the Skrunk server is quiescent,
# that is, no queries are currently being run.

for _ in {0..5}; do
	result="$(curl http://localhost:5000/quiescence 2>/dev/null | jq .in_progress)"
	if [ "$result" == 0 ] || [ "$result" == '' ]; then
		exit 0
	fi
	sleep 0.5
done

exit 1
