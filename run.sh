#!/usr/bin/env bash
cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1

json_array()
{
	local i
	local c=0
	local opt=''
	[ "$pretty" == 0 ] && opt='-n'

	echo $opt ' ['
	for i in "$@"
	do
		c=$((c+1))
		i="${i/site/}"
		[ "$c" == "$#" ] && echo $opt "    \"$i\"" || echo $opt "    \"$i\","
	done
	[ "$is_last" == 1 ] && echo $opt '  ]' || echo $opt '  ],'
}

contains()
{
	local i
	local item="$1"
	shift 1

	for i in "$@"
	do
		[ "site/$i" == "$item" ] && return 0
	done
	return 1
}

filter()
{
	local file
	while read file
	do
		contains "$file" "$@" || echo "$file"
	done
}

#Build site map for pre-loading of site resources
{
	echo '{'
	c=0
	items=(html js dot json)
	for i in "${items[@]}"
	do
		c=$((c+1))
		[ "$c" == "${#items[@]}" ] && is_last=1
		echo -n "  \"$i\":"
		[ "$i" == js ] && find="site/js/util site/js/page" || find=site

		#Don't include files that should not be cached on page load.
		json_array $(find $find -name "*.$i" -type f | filter $(cat data/no_auth_files.txt) $(cat data/no_cache_files.txt))
	done
	echo '}'
} > site/config/sitemap.json

#Generate VAPIDs
openssl ecparam -name prime256v1 -genkey -noout -out data/vapid_private.pem
openssl ec -in data/vapid_private.pem -outform DER|tail -c +8|head -c 32|base64|tr -d '=' |tr '/+' '_-' > data/private_key.txt
openssl ec -in data/vapid_private.pem -pubout -outform DER|tail -c 65|base64|tr -d '=' |tr '/+' '_-' > data/public_key.txt

#Make sure all dependencies are up to date
poetry update

#Start server
poetry run python3 main.py "$@"
