#!/usr/bin/env bash
# The baseline for the fasthex page: what the tools already on the machine print
# for the same files. fasthex is not on either CI runner, so its output lives in
# dated fences on the page; this script is the half CI checks, and every fasthex
# fence on the page is read against one of these sections.
#
# Run:  bash fasthex_baseline_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

# U+2800 plus the byte, written as UTF-8: e2, then a0 with the byte's top two
# bits, then 80 with its low six. The inner printf spells the three octal
# escapes; the outer one turns them into bytes.
braille() {
  od -An -v -tu1 "$1" | tr -s ' ' '\n' | sed '/^$/d' | while read -r b; do
    printf "$(printf '\\%03o\\%03o\\%03o' 226 $((160 | b >> 6)) $((128 | b & 63)))"
  done
  echo
}

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251: 1\342\202\254\n' > s.txt        # café: 1€ — 9 characters, 12 bytes
printf 'A\000\011\012\033\177 \303\251' > mix.bin     # one byte of each kind a text column has to draw
head -c 64 /dev/zero > zeros.bin                     # 64 bytes, all the same
yes A | tr -d '\n' | head -c 80 > runs.bin            # 80 bytes, all the same, none of them NUL
yes abcdefghijklmnopqrstuvwxyz | head -c 2100 > big.txt

echo "1. THE FILES"
show "xxd -p s.txt"
show "xxd -p mix.bin"
echo "   mix.bin is one byte of each kind: a letter, NUL, a tab, a newline, an"
echo "   escape, DEL, a space, and the two bytes of é."

echo
echo "2. THE TWO DUMPS FASTHEX'S DEFAULT IS ASSEMBLED FROM"
show "xxd s.txt"
show "hexdump -C s.txt"
echo "   xxd writes the offset with a colon and pairs the bytes; hexdump -C"
echo "   writes one cell per byte, a gap after the eighth, and the text in"
echo "   pipes. fasthex's default row is xxd's offset in front of hexdump -C's"
echo "   cells and panel — its panel padded to sixteen where hexdump's is not."

echo
echo "3. TWO BYTES AT A TIME, IN TWO ORDERS"
show "hexdump -x s.txt"
show "hexdump -d s.txt"
echo "   Both presets read the file two bytes at a time as a NUMBER, in the"
echo "   CPU's order: 63 61 becomes 0x6163, which is 24931. fasthex -X and -D"
echo "   read the same pairs in FILE order unless told -E little — 0x6361,"
echo "   which is 25441 — so the flag that makes fasthex agree with hexdump is"
echo "   the one that makes it swap. hexdump -x has no flag to do the reverse."

echo
echo "4. THE TEXT COLUMN, UNDER OTHER AGREEMENTS"
show "xxd -E s.txt"
echo "   The same twelve bytes read as EBCDIC — the column fasthex -T ebcdic"
echo "   prints. Its braille table is one glyph per byte value, U+2800 plus the"
echo "   byte, which is a rule a shell loop can apply without the tool (the"
echo "   braille function at the top of this script):"
show "braille s.txt"
echo "   and its cp437 table is the IBM PC's, which iconv knows by name, here"
echo "   for the bytes above 127:"
show "printf '\303\251\342\202\254' | iconv -f CP437 -t UTF-8; echo"

echo
echo "5. WHAT xxd -r DOES WITH A LINE THAT IS MISSING"
show "xxd runs.bin | sed '2d' | xxd -r | wc -c | tr -d ' '"
echo "   80 bytes from a dump with a row deleted: xxd -r seeks to each offset,"
echo "   so the gap is a hole of NULs and the length is unchanged. fasthex -r"
echo "   reads the hex and ignores the offsets, and the same dump comes back"
echo "   16 bytes shorter — the page has the run."

echo
echo "6. WHICH ROWS A STAR STANDS FOR"
show "hexdump -C runs.bin"
show "xxd -a runs.bin | wc -l | tr -d ' '"
echo "   hexdump collapses ANY repeated row into a star; xxd -a collapses only"
echo "   rows of NUL, so five rows of 'A' stay five rows. fasthex -w follows"
echo "   hexdump's rule, and is off unless asked."

echo
echo "7. THE FORMAT STRINGS hexdump RUNS, FOR COMPARISON WITH -F"
show "hexdump -e '16/1 \"%02x \" \"\n\"' s.txt"
show "hexdump -e '8/1 \"%02x \" \"  \" 8/1 \"%03u \" \"\n\"' s.txt"
show "hexdump -e '\"%08_ax: \" 16/1 \"%02x \" \"\n\"' s.txt"
echo "   A short last row is left short; %03u prints decimal — of the NEXT"
echo "   eight bytes, since conversions in one string consume what they print;"
echo "   and %_ax prints the offset without consuming a byte. Each of those is"
echo "   a place where fasthex -F, handed the same string, prints something else."

echo
echo "8. THE SIZE SUFFIXES ARE TWO DIFFERENT ARITHMETICS"
show "printf '%x %x\n' 2048 2000"
show "xxd -s 2048 -l 16 big.txt"
show "xxd -s 2000 -l 16 big.txt"
echo "   K and KiB are 1024; kB is 1000. fasthex -s 2K lands at 0x800 and"
echo "   -s 2kB at 0x7d0, which is the second row here."
