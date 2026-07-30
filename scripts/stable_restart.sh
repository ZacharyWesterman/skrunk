#!/usr/bin/env bash

# This script restarts the systemd service for the server with as little downtime as possible.

cd "$(dirname "${BASH_SOURCE[0]}")"/.. || exit 1

cmd="$(grep run.sh /etc/systemd/system/skrunk.service)"
args="${cmd#*run.sh }"

# Prime command to take over temporarily
poetry run python main.py $args &
pid=$?
sleep 30

# Wait a while until server is quiescent
iter=0
while ! scripts/safe_to_restart.sh; do
	iter=$((iter + 1))
	if [ "$iter" -gt 100 ]; then
		# Couldn't find time to restart server, so cancel until next restart attempt.
		kill "$pid"
		wait
		exit 1
	fi
	sleep 5
done

sudo systemctl stop skrunk
scripts/update.sh
sudo systemctl start skrunk
sleep 30

# There's always the chance server got a batch job in the middle of restart.
# Wait a while until server is quiescent, but don't wait forever.
iter=0
while ! scripts/safe_to_restart.sh; do
	iter=$((iter + 1))
	[ "$iter" -gt 100 ] && break
	sleep 5
done

kill "$pid"
wait
