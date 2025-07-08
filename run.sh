#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

json_array() {
	local i
	local c=0
	local opt=''
	[ "$pretty" == 0 ] && opt='-n'

	echo $opt ' ['
	for i in "$@"; do
		c=$((c + 1))
		i="${i/site/}"
		[ "$c" == "$#" ] && echo $opt "    \"$i\"" || echo $opt "    \"$i\","
	done
	[ "$is_last" == 1 ] && echo $opt '  ]' || echo $opt '  ],'
}

contains() {
	local i
	local item="$1"
	shift 1

	for i in "$@"; do
		[ "site/$i" == "$item" ] && return 0
	done
	return 1
}

filter() {
	local file
	while read file; do
		contains "$file" "$@" || echo "$file"
	done
}

error() {
	echo -e "\e[31mERROR:\e[0m $*"
}

warn() {
	echo -e "\e[33mWARNING:\e[0m $*"
}

#Check if dependencies are installed
#If any required dependencies are not installed, exit.
#Non-required deps will be warned about, but app will continue to run.
DEPS_ERROR=()
DEPS_WARN=()
MISSING_DEPS=0
for i in 'java 0 OpenJDK >= 8' 'python3 1 Python >= 3.10' 'poetry 1 Poetry' 'mongod 1 MongoDB >= 5'; do
	read -r program required info <<<"$i"
	if ! type "$program" &>/dev/null; then
		[ "$required" == 1 ] && DEPS_ERROR+=("$info") && MISSING_DEPS=1 || DEPS_WARN+=("$info")
	fi
done
for i in "${DEPS_ERROR[@]}"; do error "$i is not installed. Please install it."; done
for i in "${DEPS_WARN[@]}"; do warn "$i is not installed. The application will still run, but some features may not be available."; done
[ $MISSING_DEPS == 1 ] && exit 1

# If --help flag is passed just run with that flag
if [ "$1" == "--help" ]; then
	poetry run python3 main.py --help
	exit 0
fi

#Check if mongoDB is running
if ! systemctl is-active mongod &>/dev/null; then
	error "mongod service is not running! Start up the service with \`systemctl start mongod\` and then try again."
	exit 1
fi

#Build site map for pre-loading of site resources
{
	echo '{'
	c=0
	items=(html js dot json)
	for i in "${items[@]}"; do
		c=$((c + 1))
		[ "$c" == "${#items[@]}" ] && is_last=1
		echo -n "  \"$i\":"
		[ "$i" == js ] && find="site/js/util site/js/page" || find=site

		#Don't include files that should not be cached on page load.
		json_array $(find $find -name "*.$i" -type f | filter $(cat data/no_auth_files.txt) $(cat data/no_prefetch_files.txt))
	done
	echo '}'
} >site/config/sitemap.json

#Generate VAPIDs
if [ ! -e data/public_key.txt ]; then
	openssl ecparam -name prime256v1 -genkey -noout -out data/vapid_private.pem
	openssl ec -in data/vapid_private.pem -outform DER | tail -c +8 | head -c 32 | base64 | tr -d '=' | tr '/+' '_-' >data/private_key.txt
	openssl ec -in data/vapid_private.pem -pubout -outform DER | tail -c 65 | base64 | tr -d '=' | tr '/+' '_-' >data/public_key.txt
	rm -f data/vapid_private.pem
fi

#Make sure all dependencies are up to date
poetry update --without dev

#Start server
poetry run python3 main.py "$@"
