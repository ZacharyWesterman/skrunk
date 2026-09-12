#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")"/.. || exit 1

git checkout .
git clean -df
git pull --recurse-submodules
git submodule update --remote --recursive

# Make sure all dependencies are up to date
poetry update --without dev
