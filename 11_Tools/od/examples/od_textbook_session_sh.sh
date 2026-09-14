#!/usr/bin/env bash
# A textbook od session, read for what its dumps say about encoding.
# Linux books teach od on /bin/echo and on a Project Gutenberg text file. This
# builds files of the same shape -- no text from any book -- and asks od the
# questions such a chapter walks past: what the first three bytes are, what the
# leading zero in -j0000640 does, and why the first -t x word reads backwards.
#
# od -t a is not run here: GNU and BSD od print different names for the same
# high bytes (the page has both, measured), so the key shows the arithmetic
# GNU performs instead. Every od block goes through `tidy`, as in the page's
# other example, because the two implementations pad their columns differently.
#
# Run:  bash od_textbook_session_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# One space between fields, no blank lines. See od_reads_types_sh.sh, section 9.
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%s%s", (i > 1 ? " " : ""), $i; print "" }' | sed -e '/^$/d'; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"
export LC_ALL=C

# The shape of a Gutenberg plain-text file: a UTF-8 BOM, then CRLF lines, and
# one line indented with a tab. No spaces: under -t c a space prints as blanks,
# which tidy cannot tell apart from padding.
printf '\357\273\277Chapter\r\n\tIndented\r\n' > book.txt
# 000 001 002 ... 400 run together, so the digits at any offset say where
# you are: byte n is part of number n/3.
i=0
while [ "$i" -le 400 ]; do printf '%03d' "$i"; i=$((i + 1)); done > digits.txt
# The first eight bytes of a 64-bit little-endian ELF file, such as /bin/echo on
# x86-64 Linux: magic, class 64, little-endian, version 1, OS ABI 0.
printf '\177ELF\002\001\001\000' > elf.bin

echo "1. THREE BYTES BEFORE THE FIRST LETTER"
show "od -tc book.txt | tidy"
echo "   -t c prints a byte it cannot show as a character in octal. 357 273 277"
echo "   is not part of the title. In hex it is:"
show "od -An -N3 -tx1 book.txt | tidy"
echo "   ef bb bf, the UTF-8 encoding of U+FEFF: a byte order mark. And each"
echo "   line ends \\r \\n -- carriage return FIRST, then newline, the order a"
echo "   Windows editor and every CRLF protocol write them in. \\t is the tab."

echo
echo "2. WHAT GNU od -t a MAKES OF THOSE THREE BYTES"
for b in ef bb bf; do
    low=$((0x$b & 0x7f))
    # shellcheck disable=SC2059  # the format is built to print one byte
    printf "   %s & 7f = %02x   %s\n" "$b" "$low" "$(printf "\\$(printf '%03o' "$low")")"
done
echo "   GNU od -t a names the low seven bits of a byte, so a file that starts"
echo "   with a BOM starts, under -t a, with o ; ? -- three ASCII characters"
echo "   that are nowhere in it. BSD od prints ef bb bf instead. A listing that"
echo "   opens with o ; ? is GNU output of a file with a BOM."

echo
echo "3. THE LEADING ZERO MAKES -j OCTAL, NOT THE ADDRESS COLUMN"
show "od -Ad -j0400 -N8 -tc digits.txt | tidy"
show "od -Ad -j400 -N8 -tc digits.txt | tidy"
show "od -Ad -j0x190 -N8 -tc digits.txt | tidy"
echo "   -j and -N read a number the way C does: a leading 0 is octal, 0x is"
echo "   hex, anything else is decimal. The offset column is DECIMAL here"
echo "   (-A d), and -j0400 still started at byte 256, in the middle of 085."
echo "   So -j0000640 is octal because of its first zero, and -j0640 is the same"
echo "   request. It matches od's address column only because that column"
echo "   happens to be octal by default."

echo
echo "4. THE FIRST WORD OF AN ELF FILE, READ BACKWARDS"
show "od -An -tx1 elf.bin | tidy"
show "od -tx elf.bin | tidy"
show "od elf.bin | tidy"
echo "   -t x with no size is an int: four bytes, printed as one number in this"
echo "   CPU's byte order. Little-endian puts the low byte first, so the magic"
echo "   7f 45 4c 46 -- DEL E L F -- comes out as 464c457f. Bare od is -t o2,"
echo "   and 7f 45 becomes the 16-bit value 0x457f, which is 042577 in octal."
echo "   A dump of /bin/echo on 64-bit Linux opens with these same two lines."
