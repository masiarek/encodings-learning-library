#!/usr/bin/env bash
# One small file, five questions. Which tool answers which, and which columns
# are the file rather than a tool's guess about it.
#
# Run:  bash inspecting_a_file_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od lays its columns out differently on macOS (BSD) and Linux (GNU). `tidy`
# re-prints every field four wide so the same bytes give the same picture on
# both. One limit: a SPACE byte prints as blanks under -c and would vanish, so
# section 4 feeds -c an input with no spaces.
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%4s", $i; print "" }' | sed -e '/^$/d'; }

# The demo line: 'café: 1€'. Nine characters, and deliberately one of each width
# — seven 1-byte, one 2-byte (é), one 3-byte (€).
LINE='caf\303\251: 1\342\202\254\n'

# A UTF-8 locale, whatever this machine calls it. Section 3 needs one, and the
# name differs per platform (macOS has en_US.UTF-8, a bare Linux may have only
# C.UTF-8), so pick by asking each candidate what its charmap is.
utf8_locale() {
  local c
  for c in C.UTF-8 en_US.UTF-8 en_US.utf8; do
    if LC_ALL="$c" locale charmap 2>/dev/null | grep -qi 'utf-\?8'; then printf '%s' "$c"; return; fi
  done
  printf 'C'
}
UTF8=$(utf8_locale)

echo "1. THE HONEST VIEW: three tools, one file, the same twelve bytes"
show "printf '$LINE' | xxd"
show "printf '$LINE' | hexdump -C"
show "printf '$LINE' | od -An -tx1 | tidy"
echo "   Nine characters, twelve bytes. Every tool agrees, because this column IS the file."

echo
echo "2. HOW BIG IS IT? wc -c counts bytes — the same number ls -l shows in its size column"
show "printf '$LINE' | wc -c | tr -d ' '"

echo
echo "3. HOW MANY CHARACTERS? wc -m, and the answer depends on the locale"
show "printf '$LINE' | LC_ALL=C wc -m | tr -d ' '"
echo "   ^ in the C locale, 'character' means 'byte', so this is the wrong question answered 12"
show 'printf "$LINE" | LC_ALL=$UTF8 wc -m | tr -d " "'
echo "   ^ in a UTF-8 locale the same command decodes first and says 9. Same file, same tool."

echo
echo "4. od -c: the octal escape, for bytes it has no character for"
show "printf 'caf\\303\\251\\n' | od -An -tx1 -c | tidy"
echo "   c a f, then 303 251 for the é — two bytes, no character to draw for either."
echo "   (od -a, the NAMED-character row, is the one column to distrust: it is"
echo "    locale-dependent on macOS and high-bit-stripped on GNU. See the page.)"

echo
echo "5. iconv: the same nine characters, re-encoded to UTF-16 — name the byte order"
show "printf '$LINE' | iconv -f UTF-8 -t UTF-16BE | xxd"
show "printf '$LINE' | iconv -f UTF-8 -t UTF-16LE | xxd"
echo "   Same characters, mirrored bytes. Ask for plain UTF-16 and the tool chooses"
echo "   for you — big-endian on macOS, little-endian on GNU — and adds a BOM."

echo
echo "6. THE 20-BYTE FILE, rebuilt portably: a BOM, then UTF-16BE"
show "{ printf '\\376\\377'; printf '$LINE' | iconv -f UTF-8 -t UTF-16BE; } | xxd"
show "{ printf '\\376\\377'; printf '$LINE' | iconv -f UTF-8 -t UTF-16BE; } | wc -c | tr -d ' '"
echo "   12 bytes became 20: two for the BOM, two per character, for text that was"
echo "   mostly ASCII. Look at the € — its code unit is 20 ac, and xxd's text column"
echo "   shows a SPACE for that 20, because half a character still looks like a byte."

echo
echo "7. WHAT xxd SHOWS THAT THE OTHERS DO NOT"
echo "   The default pairs bytes, which draws 16-bit groups UTF-8 does not have:"
show "printf '$LINE' | xxd"
echo "   -g1 ungroups them, so each column is one byte, the way UTF-8 works:"
show "printf '$LINE' | xxd -g1"
echo "   -b for the bits (the é's two bytes both start 1, which is how UTF-8 marks them):"
show "printf '$LINE' | xxd -b"
echo "   -p for plain hex with no columns at all — the form you paste into a bug report:"
show "printf '$LINE' | xxd -p"
echo "   -s 3 -l 2 to look at two bytes 3 in, instead of dumping a whole large file:"
show "printf '$LINE' | xxd -s 3 -l 2"

echo
echo "8. THE TRAP IN hexdump's DEFAULT: no -C means 16-bit words in the CPU's OWN order"
show "printf '$LINE' | hexdump"
echo "   The file starts 63 61. That dump says 6163. Every pair is SWAPPED, because"
echo "   plain hexdump reads two bytes at a time as a number and this machine is"
echo "   little-endian. It is the same confusion UTF-16 has, in a tool that was only"
echo "   asked to show bytes. Always -C:"
show "printf '$LINE' | hexdump -C"
echo "   -e takes a format string when you want the layout under your own control,"
echo "   and unlike od's columns it comes out identical on macOS and Linux:"
show "printf '$LINE' | hexdump -e '16/1 \"%02x \" \"\\n\"'"

echo
echo "9. xxd -r: THE ONLY ONE THAT GOES BACK"
echo "   Hex in, bytes out — how to build a test file with exactly the bytes you want:"
show "echo '63 61 66 c3 a9 0a' | xxd -r -p | xxd"
echo "   And a whole dump round-trips to the file it came from:"
show "printf '$LINE' | xxd | xxd -r | xxd -p"
echo "   The point of going back is EDITING. Replace the é's two UTF-8 bytes with the"
echo "   single byte Latin-1 uses, and the file is no longer valid UTF-8:"
show "printf '$LINE' | xxd -p | sed 's/c3a9/e9/' | xxd -r -p | xxd"
echo "   Ask iconv whether it decodes (exit status only — the message differs per platform):"
show "printf '$LINE' | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1 && echo 'the original: valid UTF-8' || echo 'the original: INVALID'"
show "printf '$LINE' | xxd -p | sed 's/c3a9/e9/' | xxd -r -p | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1 && echo 'the edit: valid UTF-8' || echo 'the edit: INVALID UTF-8'"
echo "   One byte edited by hand, and the file stopped being text. That is the whole"
echo "   reason to look at bytes before blaming a program."

