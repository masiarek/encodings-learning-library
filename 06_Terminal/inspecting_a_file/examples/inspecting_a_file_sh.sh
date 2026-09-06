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
