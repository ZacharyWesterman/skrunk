#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

sphinx-apidoc -o docs/source application/ || exit 1
cd docs || exit 1
make html || exit 1
echo -e "\e[32mDocumentation generated successfully!\e[0m"
