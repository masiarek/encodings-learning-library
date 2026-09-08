#!/usr/bin/env bash
# Answer key: how long is this variable, and which two bytes never arrive?
#
# Runs under bash, like the lesson's own example, and is byte-identical on bash
# 3.2.57 (macOS) and bash 5.2.21 (ubuntu:24.04). The UTF-8 locale is looked up
# rather than named, because the two platforms share no guaranteed name; the
# name is never printed. Nothing here reads the clock, $HOME, the hostname or
# the real $USER.
set -u

tmp=$(mktemp -d)
trap 'cd /; rm -rf "$tmp"' EXIT

UTF8=""
for L in C.UTF-8 en_US.UTF-8; do
  if [ "$(LC_ALL=$L locale charmap 2>/dev/null)" = "UTF-8" ]; then UTF8=$L; break; fi
done

hex() { printf '%s' "$1" | xxd -p; }
bytes() { printf '%s' "$1" | wc -c | tr -d ' '; }

z=$(printf '\305\274')                     # ż  -- c5 bc
bad=$(printf 'a\377\376b')                 # a, two bytes that decode as nothing, b

echo "1. ONE VARIABLE, TWO LENGTHS"
LC_ALL=C
export LC_ALL
printf '   LC_ALL=C        ${#ż}=%s   ${ż#?} leaves %s\n' "${#z}" "[$(hex "${z#?}")]"
if [ -n "$UTF8" ]; then
  LC_ALL=$UTF8
  printf '   a UTF-8 locale  ${#ż}=%s   ${ż#?} leaves %s\n' "${#z}" "[$(hex "${z#?}")]"
fi
printf '   the byte count, either way: %s\n' "$(bytes "$z")"
echo "   Two answers for one unchanged variable, because \${#} is a question"
echo "   about LC_CTYPE and not about the value. The C-locale ? stripped one"
echo "   BYTE and left bc, which is half a ż and not a character at all."
echo "   printf '%s' \"\$v\" | wc -c is the count that does not move, and the"
echo "   one every shell on both platforms agreed on."

echo
echo "2. AND THE BYTES THAT ARE NOT A CHARACTER IN ANY LOCALE"
LC_ALL=C
printf '   LC_ALL=C        held=%s  ${#bad}=%s\n' "$(hex "$bad")" "${#bad}"
if [ -n "$UTF8" ]; then
  LC_ALL=$UTF8
  printf '   a UTF-8 locale  held=%s  ${#bad}=%s\n' "$(hex "$bad")" "${#bad}"
fi
echo "   Four both times, and no complaint either time. No UTF-8 sequence"
echo "   begins with ff or fe, so there is nothing there for a UTF-8 locale to"
echo "   count -- bash falls back to one per undecodable byte and moves on."
echo "   Python's str and Rust's String both refuse these bytes at the decode."
echo "   The shell has no decode: there is one type here, and it is bytes."

echo
echo "3. THE BYTE THAT NEVER ARRIVES"
LC_ALL=C
printf 'a\000b\n' > "$tmp/n.txt"
{ v=$(cat "$tmp/n.txt"); } 2>/dev/null     # bash 5 warns here, bash 3.2 is silent
printf '   the file  %s   the variable  %s   ${#v}=%s\n' "$(xxd -p < "$tmp/n.txt")" "$(hex "$v")" "${#v}"
echo "   Two, not three. The NUL was not stored and no status said so -- the"
echo "   warning is bash 5's, on stderr, and macOS's bash 3.2 prints nothing"
echo "   at all, so a script cannot portably detect this. It is not a bash"
echo "   limitation to route around either: execve takes NUL-terminated"
echo "   arguments, so the value could not be passed on even if it were held."

echo
echo "4. WHICH IS WHY THE OTHER RESERVED BYTE IS A NEWLINE"
mkdir "$tmp/box"
cd "$tmp/box"
: > 'plain.txt'
: > "$(printf 'two\nlines.txt')"
printf '   for f in $(ls)           %s\n' "$(set -- $(ls); echo "$# words")"
printf '   for f in *               %s\n' "$(set -- *; echo "$# items")"
printf '   find -print  | xargs     %s runs\n' "$(find . -type f -print  | xargs      -n1 printf '%.0sX' | wc -c | tr -d ' ')"
printf '   find -print0 | xargs -0  %s runs\n' "$(find . -type f -print0 | xargs -0 -n1 printf '%.0sX' | wc -c | tr -d ' ')"
cd "$tmp"
echo "   Two files, three words. Newline is the default record separator of"
echo "   every text channel a shell has, and it is a legal filename byte, so"
echo "   any name-carrying pipeline needs a separator that is not legal in a"
echo "   name. There is exactly one, and -print0 / -0 / -z / --null-data are"
echo "   its four spellings. The glob got two because it never serialised."

echo
echo "5. AND THE SPLIT THAT HAPPENS EVEN WHEN NOTHING IS WRONG"
LC_ALL=C
mkdir "$tmp/g"
cd "$tmp/g"
: > a.txt
: > b.txt
p='*.txt'
fields() { IFS=$2; set -- $1; printf '%s fields:' "$#"; for f in "$@"; do printf ' [%s]' "$f"; done; printf '\n'; }
printf '   var=%-8s  set -- $var -> %s   set -- "$var" -> %s\n' "'*.txt'" "$(set -- $p; echo $#)" "$(set -- "$p"; echo $#)"
printf '   default IFS on "a  b" -> %s\n' "$(fields 'a  b' "$(printf ' \t\n')")"
printf '   IFS=: on "a::b"       -> %s\n' "$(fields 'a::b' ':')"
cd "$tmp"
echo "   An unquoted expansion is re-parsed twice: split on IFS, then matched"
echo "   against the filesystem. Quoting turns both off, which is why the rule"
echo "   is quote everything rather than quote when it might have spaces --"
echo "   the *.txt case has no space in it and still came apart."
echo "   The last two lines are the rule behind the empty field: a run of"
echo "   WHITESPACE separators collapses into one, and a run of any other"
echo "   separator does not. So one two-byte character used as IFS becomes two"
echo "   separators with an empty field between them, which is the shell doing"
echo "   to a delimiter exactly what tr does to a character."
