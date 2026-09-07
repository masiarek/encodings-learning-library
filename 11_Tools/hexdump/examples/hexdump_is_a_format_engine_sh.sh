#!/usr/bin/env bash
# hexdump is not a dump tool with six views. It is a format-string engine with
# six canned format strings, and the one it runs when you type its name with no
# flags is the one that reorders your bytes.
#
# Everything here is byte-identical on macOS (BSD hexdump) and Ubuntu
# (util-linux hexdump), which is the point of the last section.
#
# Run:  bash hexdump_is_a_format_engine_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251: 1\342\202\254\n' > s.txt   # café: 1€ — 9 characters, 12 bytes
printf 'caf\351\n' > latin1.txt                 # café in Latin-1 — 5 bytes
head -c 64 /dev/zero > zeros.bin                # 64 bytes, all the same

echo "1. THE DEFAULT IS THE ONE THAT LIES"
show "hexdump s.txt"
show "hexdump -C s.txt"
echo "   The same twelve bytes, twice. The file starts 63 61; the first line"
echo "   says 6163. Every pair is swapped — and it is not a bug, it is the"
echo "   default format doing exactly what it says."

echo
echo "2. WHY: THE DEFAULT READS TWO BYTES AT A TIME, AS A NUMBER"
echo "   The preset behind a bare hexdump is 8 units of 2 bytes: 8/2 \"%04x \"."
echo "   Two bytes read as one 16-bit integer, printed in THIS CPU's byte order,"
echo "   which on anything you are likely to own is little-endian: low byte"
echo "   first. So 63 61 becomes the number 0x6163. -x is the same preset with"
echo "   wider columns:"
show "hexdump -x s.txt"
echo "   It is the UTF-16 question — which end of a two-byte number comes first —"
echo "   turning up in a tool that was only asked to show bytes."

echo
echo "3. THE PRESETS ARE FORMAT STRINGS, AND YOU CAN WRITE THEM OUT"
echo "   -C is not built in as a view. It is three -e strings, and typing them"
echo "   by hand reproduces it exactly:"
show "hexdump -e '\"%08.8_Ax\n\"' -e '\"%08.8_ax  \" 8/1 \"%02x \" \"  \" 8/1 \"%02x \"' -e '\"  |\" 16/1 \"%_p\" \"|\n\"' s.txt"
if diff <(hexdump -C s.txt) \
        <(hexdump -e '"%08.8_Ax\n"' -e '"%08.8_ax  " 8/1 "%02x " "  " 8/1 "%02x "' -e '"  |" 16/1 "%_p" "|\n"' s.txt) >/dev/null
then echo "   diff against hexdump -C: identical, byte for byte."
else echo "   diff against hexdump -C: DIFFERENT"; fi

echo
echo "4. WHY -C NEEDS THREE -e STRINGS AND NOT ONE"
echo "   Within one format string the conversions run in sequence and each one"
echo "   CONSUMES the bytes it printed. Ask one string for 16 hex bytes and then"
echo "   16 characters and it wants 32 bytes — so the text column reads past the"
echo "   end and prints nothing:"
show "hexdump -e '\"%08.8_ax  \" 8/1 \"%02x \" \"  \" 8/1 \"%02x \" \"  |\" 16/1 \"%_p\" \"|\n\"' s.txt"
echo "   The |...| came out empty. Separate -e strings are each applied to the"
echo "   SAME block of bytes, from the start — which is how one pass prints the"
echo "   same sixteen bytes as hex and again as text."

echo
echo "5. THE LAYOUT YOU ACTUALLY WANT, IN ONE STRING"
echo "   count/size \"printf format\" is the whole language: how many units, how"
echo "   many bytes each, how to print one."
show "hexdump -e '16/1 \"%02x \" \"\n\"' s.txt"
show "hexdump -e '8/1 \"%02x \" \"  \" 8/1 \"%03u \" \"\n\"' s.txt"
echo "   Two columns of the same eight bytes, hex then decimal, in a layout"
echo "   nothing else offers: od's shape is whatever its flags decided, and"
echo "   xxd's is whatever -c and -g allow. One warning about %u — write it,"
echo "   not %d. A one-byte unit under %d is SIGNED, so c3 prints as -61."

echo
echo "6. THE STAR: REPEATED LINES ARE HIDDEN BY DEFAULT"
show "hexdump -C zeros.bin"
echo "   64 bytes went in and one line came out. The * means 'and more of the"
echo "   same'. -v prints every line:"
show "hexdump -C -v zeros.bin"
echo "   Four lines of sixteen, which is the 64 bytes. Without -v the output is"
echo "   three lines — first, star, final offset — whatever the file's size, so"
echo "   the length of a dump tells you nothing about the length of the file."
echo
echo "   AND THE SQUEEZE APPLIES TO -e TOO, WHICH IS HOW IT DESTROYS DATA."
echo "   hexdump -e '1/1 \"%.2x\"' is the usual stand-in for xxd -p on a machine"
echo "   with no xxd. On this 64-byte file, characters of hex printed:"
echo -n "     hexdump -e  (no -v) : "; hexdump -e '1/1 "%.2x"' zeros.bin | wc -c | tr -d ' '
echo -n "     hexdump -ve         : "; hexdump -ve '1/1 "%.2x"' zeros.bin | wc -c | tr -d ' '
echo -n "     xxd -p              : "; xxd -p zeros.bin | tr -d '\n' | wc -c | tr -d ' '
echo "   The first one printed 00 and a star. A unit here is one byte, so any"
echo "   byte that repeats the one before it is squeezed away, and the output is"
echo "   not hex any more — it is hex with a * in it. Always write -v when the"
echo "   output is going to be parsed rather than read."

echo
echo "7. THE TEXT COLUMN IS ASCII, AND ONLY ASCII"
show "hexdump -C s.txt"
show "hexdump -C latin1.txt"
echo "   Two files, two encodings, and the same answer: a dot for every byte"
echo "   above 7f. %_p asks 'is this byte a printable ASCII character' and"
echo "   nothing else — no locale, no encoding, no guess. That is a limit and"
echo "   a virtue: the column cannot mislead you about which encoding this is,"
echo "   because it never had an opinion. Read the hex."

echo
echo "8. -c IS THE ONE VIEW THAT DOES HAVE AN OPINION"
show "hexdump -c s.txt"
echo "   Octal escapes for the bytes it cannot draw: 303 251 is the é. This runs"
echo "   under LC_ALL=C, where that is all it can do. In a UTF-8 locale BSD"
echo "   hexdump prints M-C M-) here and Ubuntu's still prints 303 251 — the"
echo "   page has the measurement. Same command, two machines, two answers."

echo
echo "9. WHAT IT CANNOT DO: COME BACK"
show "xxd -p s.txt"
show "xxd -p s.txt | xxd -r -p | cat"
echo "   xxd -r reads a dump and writes the bytes. hexdump has no -r and od has"
echo "   no -r; to reverse a hexdump you write the loop yourself. That single"
echo "   missing flag is the reason to install xxd on a machine that lacks it."

echo
echo "10. SKIP AND LENGTH, WHEN THE INTERESTING BYTES ARE NOT AT THE FRONT"
show "hexdump -C -s 2 -n 4 s.txt"
echo "   -s skips, -n stops after that many bytes, and the offset column keeps"
echo "   counting from the front of the file — so what it prints is the address"
echo "   in the file, not in the window. xxd spells the same two -s and -l."
