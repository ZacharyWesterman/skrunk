#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")"/.. || exit 1

git remote update

local=$(git rev-parse @)
remote=$(git rev-parse origin)
base=$(git merge-base @ origin)

if [ "$local" == "$remote" ]; then
    echo >&2 "Up-to-date"
elif [ "$local" == "$base" ]; then
    echo >&2 "Need to pull"
	exit 0
elif [ "$remote" == "$base" ]; then
    echo >&2 "WARNING: Local is ahead of remote!?"
else
    echo >&2 "WARNING: Local and remote have diverged!?"
fi

exit 1
