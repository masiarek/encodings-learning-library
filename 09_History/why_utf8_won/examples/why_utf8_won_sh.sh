#!/usr/bin/env bash
# The practical half of the argument: the tools you already have keep working.
#
# Everything below is run under LC_ALL=C — no locale, no Unicode awareness in
# any of these tools at all. They still get the right answer on UTF-8 text,
# because UTF-8 was designed so that they would.
#
# Run:  bash why_utf8_won_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

ROW='id,Łódź,日本語,ok'

echo "1. ASCII-ONLY TOOLS, ON TEXT THEY HAVE NEVER HEARD OF"
echo "   The row: $ROW"
show "printf '%s\\n' \"\$ROW\" | cut -d, -f2"
show "printf '%s\\n' \"\$ROW\" | cut -d, -f3"
show "printf '%s\\n' \"\$ROW\" | awk -F, '{print NF \" fields\"}'"
show "printf '%s\\n' \"\$ROW\" | grep -c 'id'"
echo "   cut, awk and grep split on the byte 0x2c. In UTF-8 that byte can only"
echo "   ever be a real comma, so none of them can cut a character in half."

echo
echo "2. THE SAME ROW AS UTF-16, HANDED TO THE SAME TOOLS"
show "printf '%s' \"\$ROW\" | iconv -f UTF-8 -t UTF-16LE | xxd -p | head -2"
printf '   cut -d, -f2 on that gives : '
printf '%s' "$ROW" | iconv -f UTF-8 -t UTF-16LE | cut -d, -f2 | xxd -p
echo "   Bytes, not text — and every other byte is 00, which is what ends a"
echo "   string in C. Adopting UTF-16 in 1993 would have meant rewriting every"
echo "   tool on the machine on the same day. Adopting UTF-8 meant rewriting"
echo "   none of them."

echo
echo "3. SORTING BY RAW BYTES IS ALREADY THE RIGHT ORDER"
echo "   Five characters, deliberately out of order, sorted by BYTE value"
echo "   with no locale at all:"
show "printf 'z\\né\\nA\\n日\\n0\\n' | LC_ALL=C sort"
echo "   That is exactly their Unicode order: 0 (U+0030), A (U+0041),"
echo "   z (U+007A), é (U+00E9), 日 (U+65E5). A byte sort, a byte-wise binary"
echo "   search and a plain B-tree index are all correct on UTF-8 without"
echo "   knowing a thing about Unicode."

echo
echo "4. AND THE COUNTING TRAP THAT NEVER WENT AWAY"
show "printf '%s' 'Łódź' | wc -c | tr -d ' '"
echo "   Seven bytes, four letters. wc -c counts bytes and always did; it is"
echo "   the database column, the fixed-width field and the substring that"
echo "   still need to be told which of the two they meant."
