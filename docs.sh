#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

[ "$1" == "--clean" ] && echo -e "\e[33mCleaning up old documentation...\e[0m" && rm -rf docs/build docs/source/application.*.rst

echo -e "\e[34mGenerating documentation...\e[0m"

sphinx-apidoc -o docs/source application application/tags || exit 1
cd docs || exit 1

if [ "$1" == "--coverage" ]; then
	SPHINXOPTS="-b coverage" make html || exit 1
else
	make html || exit 1
	echo -e "\e[32mDocumentation generated successfully!\e[0m"
fi
