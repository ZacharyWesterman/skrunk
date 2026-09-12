#!/usr/bin/env bash

# This script restarts the systemd service for the server with as little downtime as possible.

cd "$(dirname "${BASH_SOURCE[0]}")"/.. || exit 1

echo -n >&2 "Checking for update..."
if ! scripts/needs_update.sh &>/dev/null; then
	exit 0
fi

# Wait a while until server is quiescent
iter=0
while ! scripts/safe_to_restart.sh; do
	iter=$((iter + 1))
	if [ "$iter" -gt 100 ]; then
		# Couldn't find time to restart server, so cancel until next restart attempt.
		echo >&2 "Couldn't find a safe time to restart, cancelling!"
		exit 1
	fi
	sleep 5
done

scripts/update.sh
sudo systemctl restart skrunk

