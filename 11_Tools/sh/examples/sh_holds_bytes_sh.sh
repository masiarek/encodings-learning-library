#!/usr/bin/env bash
# The shell has no string type: a variable holds bytes, two of which are
# reserved by the machinery around it.
#
# Everything here runs under bash, because that is what this library's runner
# runs, and every line below is byte-identical on bash 3.2.57 (macOS) and bash
# 5.2.21 (ubuntu:24.04). What the OTHER shells do -- dash, which is Ubuntu's
# /bin/sh, and bash-invoked-as-sh, which is a Mac's -- is on the page in dated
# fences, because no answer key can hold both.
#
# The locale is set inside the script, section by section, on purpose: this
# lesson's subject IS the locale, so it cannot inherit the runner's LC_ALL=C.
# The UTF-8 locale is looked up rather than named, because macOS and
# ubuntu:24.04 have no UTF-8 locale name in common that is guaranteed present
# -- and its name is never printed, so the key does not depend on which one was
# found.
#
# Nothing the reader's machine supplies reaches the output. USER is pinned to
# 'ada' below so section 1 prints the same bytes everywhere; there is no clock,
# no hostname and no $HOME anywhere in this file.
#
# Run:  bash sh_holds_bytes_sh.sh
set -u

USER=ada                                   # pinned; see the note above
export USER

tmp=$(mktemp -d)
trap 'cd /; rm -rf "$tmp"' EXIT

# The first locale in this list whose charmap really is UTF-8. macOS 26 has
# C.UTF-8 and en_US.UTF-8; ubuntu:24.04 has only C.UTF-8. An absent locale is
# not an error on either platform -- it silently falls back to ASCII -- so the
# charmap has to be asked for rather than assumed.
UTF8=""
for L in C.UTF-8 en_US.UTF-8; do
  if [ "$(LC_ALL=$L locale charmap 2>/dev/null)" = "UTF-8" ]; then UTF8=$L; break; fi
done

hex() { printf '%s' "$1" | xxd -p; }       # the bytes of a value, never its picture
bytes() { printf '%s' "$1" | wc -c | tr -d ' '; }   # tr -d strips BSD wc's padding
# One aligned row, with no trailing spaces when the third column is empty --
# a recorded key that ends in whitespace is a key nobody can see is wrong.
row() { if [ -n "$3" ]; then printf '   %-22s %-9s%s\n' "$1" "$2" "$3"; else printf '   %-22s %s\n' "$1" "$2"; fi; }

echo "1. A VARIABLE HOLDS BYTES, AND NOTHING CHECKS THEM"
good=$(printf 'caf\303\251')               # café, valid UTF-8
bad=$(printf 'a\377\376b')                 # a, two bytes that are not UTF-8, b
printf '   good=%s   bad=%s\n' "$(hex "$good")" "$(hex "$bad")"
printf '   $USER=%s (pinned)   its bytes=%s\n' "$USER" "$(hex "$USER")"
echo "   The second assignment did not fail, warn, or replace anything: no"
echo "   UTF-8 sequence begins with ff or fe, and the shell stored them"
echo "   anyway. There is no other value here -- no str, no String, no"
echo "   bytes-versus-text pair. A shell variable is a byte string, and an"
echo "   environment variable is the same byte string one execve further on."

echo
echo "2. SO WHAT DOES \${#var} COUNT?"
LC_ALL=C
export LC_ALL
z=$(printf '\305\274')                     # ż, two bytes
printf '   LC_ALL=C        ${#café}=%s  ${#ż}=%s\n' "${#good}" "${#z}"
if [ -n "$UTF8" ]; then
  LC_ALL=$UTF8
  printf '   a UTF-8 locale  ${#café}=%s  ${#ż}=%s\n' "${#good}" "${#z}"
fi
printf '   the bytes, either way: café=%s  ż=%s\n' "$(bytes "$good")" "$(bytes "$z")"
echo "   \${#var} is not a length. It is a question about the locale, and it"
echo "   has two answers for one unchanged variable. The byte count is the"
echo "   one number that does not move, and the portable way to ask for it is"
echo "   the third line: printf '%s' \"\$v\" | wc -c."

echo
echo "3. AND EVERY OTHER EXPANSION ASKS THE SAME QUESTION"
LC_ALL=C
printf '   LC_ALL=C        ${café:3:1}=%-6s ${ż#?}=%-4s case ż in ?) ' "$(hex "${good:3:1}")" "$(hex "${z#?}")"
case $z in ?) echo "matches";; *) echo "no match";; esac
if [ -n "$UTF8" ]; then
  LC_ALL=$UTF8
  printf '   a UTF-8 locale  ${café:3:1}=%-6s ${ż#?}=%-4s case ż in ?) ' "$(hex "${good:3:1}")" "$(hex "${z#?}")"
  case $z in ?) echo "matches";; *) echo "no match";; esac
fi
echo "   In the C locale the substring took HALF of the é and the ? stripped"
echo "   half of the ż, leaving an orphan bc that is not text any more. This"
echo "   is tr's failure mode with no tool involved: the cut happened inside"
echo "   the shell, in an expansion that looks like string slicing."

echo
echo "4. THE FIRST BYTE THE SHELL CANNOT CARRY: NUL"
LC_ALL=C
printf 'a\000b\n' > "$tmp/n.txt"
{ v=$(cat "$tmp/n.txt"); } 2>/dev/null     # bash 5 warns here, bash 3.2 is silent
lit=$'a\x00b'
row 'on disk'               "$(xxd -p < "$tmp/n.txt")"  ''
row 'through $(...)'        "$(hex "$v")"               "len=${#v}"
row "through \$'a\\x00b'"     "$(hex "$lit")"             "len=${#lit}"
row 'out through an execve' "$(env X="$v" sh -c 'printf %s "$X"' | xxd -p)" ''
echo "   Three different amputations of one three-byte string, none of them an"
echo "   error. \$(...) drops the NUL and keeps going; \$'...' stops dead at it;"
echo "   and execve could not have carried it in the first place, which is the"
echo "   kernel's rule rather than the shell's. That is why -print0 exists."

echo
echo "5. THE SECOND: NEWLINE, WHICH IS THE DEFAULT FIELD SEPARATOR"
mkdir "$tmp/box"
cd "$tmp/box"
: > 'plain.txt'
: > "$(printf 'two\nlines.txt')"           # a legal filename on both platforms
printf '   two files on disk:       %s\n' "$(find . -type f | LC_ALL=C sort | xxd -p | tr -d '\n')"
printf '   for f in $(ls)           %s words\n' "$(set -- $(ls); echo $#)"
printf '   for f in *               %s items\n' "$(set -- *; echo $#)"
printf '   find -print  | xargs     %s runs\n' "$(find . -type f -print  | xargs      -n1 printf '%.0sX' | wc -c | tr -d ' ')"
printf '   find -print0 | xargs -0  %s runs\n' "$(find . -type f -print0 | xargs -0 -n1 printf '%.0sX' | wc -c | tr -d ' ')"
cd "$tmp"
echo "   The loop is not the bug. \$(ls) and a bare xargs both went through a"
echo "   channel whose record separator is a newline, and one of these files"
echo "   contains a newline -- so two names arrived as three. The glob never"
echo "   serialised at all, and -print0 serialised with the one separator a"
echo "   filename cannot contain, so both of those counted two."

echo
echo "6. IFS IS A SET OF BYTES, NOT A DELIMITER"
show_split() {
  s=$(printf 'a\303\251b')                 # a é b
  IFS=$(printf '\303\251')                 # IFS is the two bytes of é
  set -- $s
  printf '%s fields:' "$#"
  for f in "$@"; do printf ' [%s]' "$(hex "$f")"; done
  printf '\n'
  IFS=$(printf ' \t\n')
}
LC_ALL=C
printf '   LC_ALL=C        IFS=é on "aéb" -> %s\n' "$(show_split)"
if [ -n "$UTF8" ]; then
  LC_ALL=$UTF8
  printf '   a UTF-8 locale  IFS=é on "aéb" -> %s\n' "$(show_split)"
fi
echo "   Three fields in the C locale, and the middle one is empty: both bytes"
echo "   of the é were separators, so one character became two delimiters with"
echo "   nothing between them. IFS is a SET, exactly like tr's argument, and"
echo "   the locale is the only thing deciding whether it is a set of bytes or"
echo "   a set of characters. Use a single-byte separator and the question"
echo "   never comes up."

echo
echo "7. WHICH IS WHY ONE UNQUOTED EXPANSION IS THE WHOLE CLASS"
LC_ALL=C
mkdir "$tmp/g"
cd "$tmp/g"
: > a.txt
: > b.txt
p='*.txt'
q='one  two'
printf '   var=%-12s set -- $var -> %s  |  set -- "$var" -> %s\n' "'*.txt'"   "$(set -- $p; echo $#)" "$(set -- "$p"; echo $#)"
printf '   var=%-12s set -- $var -> %s  |  set -- "$var" -> %s\n' "'one  two'" "$(set -- $q; echo $#)" "$(set -- "$q"; echo $#)"
cd "$tmp"
echo "   An unquoted expansion is not a value being read. It is a value being"
echo "   re-parsed: split on IFS, then matched against the filesystem. Quoting"
echo "   it turns both off, which is the whole of the advice -- and the reason"
echo "   the advice is not 'quote when the value might have spaces'."

echo
echo "8. echo IS NOT PORTABLE. printf IS."
row 'printf "caf\303\251"'  "$(printf 'caf\303\251' | xxd -p)"       ''
row 'echo   "caf\303\251"'  "$(echo 'caf\303\251' | xxd -p)"         ''
row "\$'caf\\xc3\\xa9'"          "$(printf '%s' $'caf\xc3\xa9' | xxd -p)"  ''
echo "   Line one is six bytes on every shell this library has measured. Line"
echo "   two is bash's echo leaving the backslashes alone -- and dash's echo,"
echo "   which is /bin/sh on Ubuntu, expands them instead, so the same command"
echo "   writes a different file. Line three is bash's own \$'...' quoting,"
echo "   which dash does not have at all: it prints a dollar sign and the"
echo "   backslashes, and says nothing. printf with octal escapes is the one"
echo "   spelling that means the same thing everywhere."
