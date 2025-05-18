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

# Stash changes that would not be included in the commit.
git stash -q --include-untracked --keep-index

# Check if graphql schema is valid.
echo >&2 "Checking GraphQL schema..."
gql_ok=1
if ! scripts/schema_check.py; then
	echo >&2 -e "\e[31mERROR:\e[0m The GraphQL schema is invalid."
	echo >&2 -e "\e[34mPlease fix the errors and try again.\e[0m"
	error=1
	gql_ok=0
fi

# Check if types have changed and need to be generated.
if [ \$gql_ok -eq 1 ]; then
	echo >&2 "Checking GraphQL types..."
	t="\$(scripts/build_types.py check)"
	if [ "\$t" != '' ]; then
		echo >&2 -e "\e[31mERROR:\e[0m The GraphQL schema changed for the type(s) [\$t]."
		echo >&2 -e "\e[34mPlease run \`scripts/build_types.py\` to update the types, then add those file(s) to the commit.\e[0m"
		error=1
	fi
fi

git stash pop -q

[ \$error -eq 0 ] || commit_fail

echo >&2 -e "\e[32mAll checks passed. Proceeding with commit.\e[0m"

EOF
