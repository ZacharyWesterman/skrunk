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
		[ "$c" == "$#" ] && echo $opt "    \"/$i\"" || echo $opt "    \"/$i\","
	done
	[ "$is_last" == 1 ] && echo $opt '  ]' || echo $opt '  ],'
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
		[ "$i" == js ] && find=site/js/page || find=site
		json_array $(find "$find" -name "*.$i" -type f)
	done
	echo '}'
} > site/config/sitemap.json


#Start server
poetry run python3 main.py "$@"
