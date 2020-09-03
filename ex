#!/bin/bash
set -e

# ex - unpack archives while preserving metadata
# ed <irc.rizon.net>, MIT-licensed, https://github.com/9001/usr-local-bin
# -- creates a toplevel folder for the extracted files only if necessary
#
# optional args after archive name:
#   r = remove archive after unpack
#   n = no trust name inside archive (always subfolder based on archive filename)
# suggested usage:
#   for f in *; do case "$f" in *.rar | *.zip | *.7z ) ex ./"$f" r || break ;; esac; done


export TZ=UTC+0
export LC_ALL=en_US.UTF-8


arc="$1"
[ -e "$arc" ] || {
	echo "need arg 1: archive to unpack" >&2
	exit 1
}

# make archive path absolute
case "$arc" in
	/*) ;;
	*) arc="$PWD/$arc" ;;
esac
[ -e "$arc" ] || {
	echo "error: could not determine absolute path to archive" >&2
	exit 1
}


# subfolder name = archive name sans extension
name="${1##*/}"
name="${name%.*}"
[ -z "$name" ] && {
	echo "error: could not determine folder name" >&2
	exit 1
}


shift
printf '\033[36m[*] archive: \033[0m%s\033[7m$\033[0m\n' "$arc" >&2
printf '\033[36m[*]  folder: \033[0m%s\033[7m$\033[0m\n' "$name" >&2


# fails if folder exists
mkdir "./$name"
cd "./$name"


# see if we can unbuffer
command -v stdbuf >/dev/null &&
	ub='stdbuf -i0 -o0 -e0' || ub=


# collect some metadata;
# unrar shows password prompt on stderr
#    7z shows password prompt on stdout
ts=$(date +%s)
$ub unrar lta "$arc" 2>&1 | $ub tee .arcex-$ts-rar | $ub tr : '\n' | $ub awk '/Enter password/'
$ub 7z l -slt "$arc" 2>&1 | $ub tee .arcex-$ts-7z  | $ub tr : '\n' | $ub awk '/Enter password/'

tee <"$arc" >(
	md5sum >/dev/shm/.$ts.$$.m5)   >(
	sha1sum >/dev/shm/.$ts.$$.s1)  >(
	sha256sum >/dev/shm/.$ts.$$.s2) |
	sha512sum >/dev/shm/.$ts.$$.s5

(
	stat "$arc" 2>&1
	echo
	cat /dev/shm/.$ts.$$.*
) > .arcex-$ts-arc

rm /dev/shm/.$ts.$$.*


# if the top-level archive entry is a singe folder
# with the same name as the archive, then don't nest

cat >/dev/null <<'EOF'
(
	awk '/^ +Name: / {sub(/[^:]+: /,"");print}' < .arcex-$ts-rar
	awk '/^Path = / && n++>0 {sub(/[^=]+= /,"");print}' < .arcex-$ts-7z
) |
awk -v name="$name" '
	{hit++; p=substr($0, 1, length(name)+1)}
	$0 == name || p == name "/" {ok++}
	0 {printf "%d %d\n[%s]\n[%s]\n[%s]\n[%s]\n", hit, ok, $0, name, p, name "/"}
	END {if (hit<2 || ok<2 || hit!=ok) {exit 1}}
' && {
	echo "[*] single subfolder matching archive name; will not nest" >&2
	log="./$name/"
	cd ..
} || {
	echo "[!] multiple top-level items (or name mismatch); creating subfolder" >&2
	log="./"
}
EOF

arctop="$((
	awk '/^Path = / && n++>0 {sub(/[^=]+= /,"");print}' < .arcex-$ts-7z
	#awk '!/^ +Name: / {next} {sub(/[^:]+: /,"")} !/^(CMT|RR)$/' < .arcex-$ts-rar
	awk '/^ +Name: / {sub(/^[^:]+: /,"");n=$0;next} /^ +Type: (File|Directory)$/ {f=1;next} /^$/&&n&&f {print n;f=0;n=""}' < .arcex-$ts-rar
) |
awk -F/ '
	k != $1 {k=$1; nk++}
	END {if (nk==1) {print k}}
')"

log="./"

if [ "$arctop" = "$name" ]; then
	printf "\033[36m[*] single subfolder matching archive name; will not nest\033[0m\n" >&2
	log="./$name/"
	cd ..

elif [ -z "$arctop" ]; then
	printf "\033[33m[!] multiple top-level items; creating subfolder\033[0m\n" >&2

else
	printf "\033[33m[!] filename does not match the top-level dir inside archive:\033[0m\n"
	printf '\033[36m[*] expect: \033[0m%s\033[7m$\033[0m\n' "$name"
	printf '\033[36m[*]  found: \033[0m%s\033[7m$\033[0m\n' "$arctop"
	
	if [ -e "../$arctop" ]; then
		printf "\033[35m[!] cannot use suggested name (exists)\033[0m\n"
	else
		while true; do
			printf '\033[1;37m[?] use suggested name (top-level dir inside archive)? [Y/n]: \033[0m'
			r=n
			printf '%s\n' "$*" | grep -qE '(^| )n( |$)' ||
				read -n1 -r r
			
			echo
			printf '%s' "$r" | grep -qE '^[yYnN]$' && break
		done
		printf '%s' "$r" | grep -qE '^[yY]$' && {
			cd ..
			mv "./$name" "./$arctop"
			name="$arctop"
			log="./$name/"
		}
	fi
fi


rv=300


# use unrar if .rar
[ "${arc##*.}" = "rar" ] && {
	$ub unrar x -kb "$arc" 2>&1 | $ub tee "$log.arcex-$ts-ex"
	rv=${PIPESTATUS[0]}
}


# use 7z if .7z or .zip
[ "${arc##*.}" = "7z" ] ||
[ "${arc##*.}" = "zip" ] && {
	$ub 7z x "$arc" 2>&1 | $ub tee "$log.arcex-$ts-ex"
	rv=${PIPESTATUS[0]}
}


if [ $rv -eq 300 ]; then
	printf '\033[1;31m[X] unsupported archive format\033[0m\n'
	exit 1
elif [ $rv -ne 0 ]; then
	printf '\033[1;31m[X] error %d\033[0m\n'
	echo $rv > "$log.arcex-$ts-ERROR"
	exit $rv
fi


#[ "$2" = "r" ] &&
printf '%s\n' "$*" | grep -qE '(^| )r( |$)' &&
	rm "$arc"


printf '\033[32mok\033[0m\n'
