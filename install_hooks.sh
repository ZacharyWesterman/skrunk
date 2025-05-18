#!/usr/bin/env bash
# This script installs the pre-commit hooks for the project.

pre-commit install

cat <<EOF >.git/hooks/pre-commit
#!/usr/bin/env bash

error=0
commit_fail() {
	echo >&2 -e "\e[31mCommit aborted. Please fix any errors and try again.\e[0m $1"
	exit 1
}

# Check if types have changed and need to be generated.
echo >&2 "Checking GraphQL types..."
t="\$(./build_types.py check)"
if [ "\$t" != '' ]; then
	echo >&2 -e "\e[31mERROR:\e[0m The GraphQL schema changed for the type(s) [\$t]."
	echo >&2 -e "\e[34mPlease run ./build_types.py to update the types.\e[0m"
	error=1
fi

[ \$error -eq 0 ] || commit_fail

EOF
