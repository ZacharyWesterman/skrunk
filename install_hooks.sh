#!/usr/bin/env bash
# This script installs the pre-commit hooks for the project.

pre-commit install
cp scripts/pre-commit .git/hooks/pre-commit
