#!/usr/bin/env bash

dev=0
prod=0
ldap=0
docs=0

for i in "$@"; do
	case "$i" in
		ldap) ldap=1 ;;
		prod) prod=1 ;;
		dev) dev=1 ;;
		docs) docs=1 ;;
		*)
			echo >&2 "ERROR: unkown option \`$i\`. Valid options are \`dev\`, \`prod\`, \`docs\` and \`ldap\`."
			exit 1
		;;
	esac
done

if [ "$dev$prod" == "00" ]; then
	echo >&2 "ERROR: Either \`dev\` or \`prod\` must be selected!"
	exit 1
fi

if [ "$dev$prod" == "11" ]; then
	echo >&2 "ERROR: Either \`dev\` or \`prod\` must be selected, not both!"
	exit 1
fi

apt_packages=(libjpeg-dev ffmpeg python3 python3-poetry openjdk-25-jre)
poetry_flags=(--no-root)

[ "$docs" == 0 ] && poetry_flags+=(--without dev)
[ "$ldap" == 1 ] && apt_packages+=(libldap2-dev libssl-dev libsasl2-dev)
[ "$ldap" == 1 ] && poetry_flags+=(-E ldap)

if [ ! -d site/js/libs/pdf.js ]; then
	rm -f .pdf.js.zip
	wget https://github.com/mozilla/pdf.js/releases/download/v6.3.289/pdfjs-6.3.289-dist.zip -O .pdf.js.zip
	unzip -o -d site/js/libs/pdf.js .pdf.js.zip
	rm -f .pdf.js.zip
fi

sudo apt install "${apt_packages[@]}"
poetry install "${poetry_flags[@]}"
