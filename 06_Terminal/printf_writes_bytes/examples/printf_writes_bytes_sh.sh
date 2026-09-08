#!/usr/bin/env bash
# printf writes exactly the bytes you name, and echo does not.
#
# Everything recorded here is byte-identical on macOS (bash 3.2.57) and Ubuntu
# (bash 5.2.21). The one construct that is NOT is \u — the escape that names a
# CODE POINT rather than a byte — so section 4 records only its LENGTH, and the
# three answers it actually gives are in a dated table on the page.
#
# Run:  bash printf_writes_bytes_sh.sh
set -u

hx() { od -An -tx1 | tr -d '\n' | tr -s ' ' | sed 's/^ *//; s/ *$//'; }
n()  { wc -c | tr -d ' '; }          # wc pads its count differently on the two

echo "1. ONE CHARACTER, SIX WAYS TO WRITE ITS TWO BYTES"
echo "   e-acute is c3 a9 in UTF-8. Every line below puts those two bytes on"
echo "   the pipe and nothing else — no newline, no eighth bit turned on by"
echo "   accident, no locale consulted."
printf "   %-30s %s\n" "printf '\\xc3\\xa9'"        "$(printf '\xc3\xa9'      | hx)"
printf "   %-30s %s\n" "printf '\\303\\251'"        "$(printf '\303\251'      | hx)"
printf "   %-30s %s\n" "printf '%b' '\\xc3\\xa9'"   "$(printf '%b' '\xc3\xa9' | hx)"
printf "   %-30s %s\n" "printf '%b' '\\0303\\0251'" "$(printf '%b' '\0303\0251' | hx)"
printf "   %-30s %s\n" "printf '%s' \$'\\xc3\\xa9'" "$(printf '%s' $'\xc3\xa9' | hx)"
printf "   %-30s %s\n" "xxd -r -p <<< c3a9"          "$(xxd -r -p <<< 'c3a9'   | hx)"
echo "   \xHH is hex and \NNN is octal. Octal is the POSIX spelling and hex is"
echo "   a bash extension, so a script that must run under /bin/sh writes 303"
echo "   251 — which is why old code is full of octal nobody enjoys reading."

echo
echo "2. WHERE THE ESCAPES ARE READ, AND WHERE THEY ARE NOT"
printf "   %-30s %s\n" "printf '\\x41'"       "$(printf '\x41'       | hx)"
printf "   %-30s %s\n" "printf '%s' '\\x41'"  "$(printf '%s' '\x41'  | hx)"
printf "   %-30s %s\n" "printf '%b' '\\x41'"  "$(printf '%b' '\x41'  | hx)"
printf "   %-30s %s\n" "printf '\\101'"       "$(printf '\101'       | hx)"
printf "   %-30s %s\n" "printf '%s' '\\101'"  "$(printf '%s' '\101'  | hx)"
printf "   %-30s %s\n" "printf '%b' '\\101'"  "$(printf '%b' '\101'  | hx)"
echo "   The FORMAT string is always read for escapes. An ARGUMENT is read for"
echo "   them only under %b — under %s it is five literal bytes, 5c 78 34 31,"
echo "   a backslash and three ASCII characters. That is the difference, and"
echo "   it is the reason %b exists at all."

echo
echo "3. THE STRING YOU CANNOT ECHO"
printf "   %-30s [%s]\n" "echo '-n'"            "$(echo '-n'            | hx)"
printf "   %-30s [%s]\n" "echo '-e'"            "$(echo '-e'            | hx)"
printf "   %-30s [%s]\n" "printf '%s\\n' '-n'"  "$(printf '%s\n' '-n'    | hx)"
printf "   %-30s [%s]\n" "echo 'a\\tb'"         "$(echo 'a\tb'          | hx)"
echo "   The first line printed NOTHING — not the two characters, not even a"
echo "   newline. echo read '-n' as its own option, which is what it is for."
echo "   There is no quoting that gets it back: the argument is gone before"
echo "   echo starts. printf has no options after the format, so '-n' is data."

echo
echo "4. THE ESCAPE THAT NAMES A CODE POINT, AND WHY IT IS NOT HERE"
printf "   %-34s %s bytes\n" "printf '\\u20ac'  (a CODE POINT)" "$(printf '\u20ac' | n)"
printf "   %-34s %s bytes\n" "printf '\\xe2\\x82\\xac' (BYTES)" "$(printf '\xe2\x82\xac' | n)"
printf "   %-34s %s\n" "is the \u output pure ASCII?" \
  "$(printf '\u20ac' | LC_ALL=C tr -d '\000-\177' | n | sed 's/^0$/yes — so it is NOT a euro/; s/^[1-9].*/no/')"
echo "   Six bytes where three were wanted. This machine handed the escape"
echo "   back as text instead of encoding it, and a different bash on a"
echo "   different locale hands back six DIFFERENT bytes or three correct"
echo "   ones. Three configurations, three answers, one of them a euro sign."
echo "   The table is on the page. \xHH and \NNN ask the locale nothing and"
echo "   are identical everywhere, which is why this library writes bytes."

echo
echo "5. THE FORMAT IS REUSED UNTIL THE ARGUMENTS RUN OUT"
printf "   %-30s %s\n" "printf '%s-' a b c"   "$(printf '%s-' a b c | hx)"
printf "   %-30s %s\n" "printf '<%s>' a"      "$(printf '<%s>' a    | hx)"
printf "   %-30s %s\n" "printf '<%s>'"        "$(printf '<%s>'      | hx)"
echo "   With three arguments the format ran three times; with none it ran"
echo "   once and %s took the empty string. That is a loop you did not write,"
echo "   and it is why printf DATA is a bug: a '%' inside the data becomes a"
echo "   conversion. Put the data in an argument — printf '%s' \"\$var\" —"
echo "   never in the format."

echo
echo "6. THE ONE BYTE A SHELL VARIABLE CANNOT CARRY"
printf "   %-34s %s\n" "printf 'a\\000b' > f  then wc -c < f" "$(printf 'a\000b' > f; n < f)"
printf "   %-34s %s\n" "the file's bytes"                  "$(hx < f)"
# The shell itself warns about the dropped NUL from bash 4.4 onward, and bash
# 3.2 does not — a diagnostic no key could hold, so fd 2 is parked for one
# line. The warning is emitted during expansion, which is why a redirection on
# the assignment itself does not catch it. The version table is on the page.
exec 3>&2 2>/dev/null
v=$(printf 'a\000b')
exec 2>&3 3>&-
printf "   %-34s %s\n" "v=\$(printf 'a\\000b'); printf %s \"\$v\"" "$(printf '%s' "$v" | hx)"
rm -f f
echo "   printf wrote the NUL and the file kept it. The command substitution"
echo "   did not: \$( ) drops NUL bytes, so the same three bytes came back as"
echo "   two. Build bytes with printf by all means — but redirect them to a"
echo "   file, because a shell variable is the one container on this page"
echo "   that cannot hold every byte."

echo
echo "7. AND BACK AGAIN"
printf 'caf\303\251\n' > round.bin
printf "   %-30s %s\n" "the file"          "$(hx < round.bin)"
printf "   %-30s %s\n" "xxd -p round.bin"  "$(xxd -p round.bin)"
printf "   %-30s %s\n" "then xxd -r -p"      "$(xxd -p round.bin | xxd -r -p | hx)"
printf "   %-30s %s\n" "cat -v round.bin"  "$(cat -v round.bin | tr -d '\n')"
echo "   xxd -p and xxd -r -p are printf's round trip: bytes to a hex string"
echo "   you can paste into a bug report, and back to the same bytes. cat -v"
echo "   is the third view — M-C M-) is c3 a9 with the high bit named rather"
echo "   than drawn, which is the form that survives an email."
rm -f round.bin
