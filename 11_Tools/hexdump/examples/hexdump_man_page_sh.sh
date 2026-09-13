#!/usr/bin/env bash
# The rules in hexdump(1) that the presets hide: what a bare %x eats, what
# happens when the input runs out mid-format, which string sets the block
# size, and the escapes hexdump added to printf.
#
# Everything here is byte-identical on macOS (BSD hexdump) and Ubuntu
# (util-linux hexdump); both man pages describe the same engine.
#
# Run:  bash hexdump_man_page_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'abcdefgh' > eight.bin          # 61 62 63 64 65 66 67 68
printf 'abc' > three.bin               # 61 62 63
printf 'a' > one.bin                   # 61
printf 'a\tb\n\0\177' > ctl.bin        # a TAB b LF NUL DEL — six bytes
printf 'caf\303\251: 1\342\202\254\n' > s.txt   # café: 1€ — 12 bytes

echo "1. A BARE %x EATS FOUR BYTES, NOT ONE"
show "hexdump -e '\"%x \"' eight.bin; echo"
show "hexdump -e '/1 \"%x \"' eight.bin; echo"
echo "   The man page's table: %d %i %o %u %X %x default to a FOUR-byte unit, and"
echo "   1, 2 and 4 are the only sizes allowed. 64636261 is 'abcd' read as one"
echo "   little-endian 32-bit number — the bare-hexdump swap, twice as wide. Write"
echo "   the byte count every time: /1 for bytes."

echo
echo "2. THE INPUT RUNS OUT MID-FORMAT: THE BLOCK IS ZERO-PADDED"
show "hexdump -e '2/2 \"%04x \" \"\n\"' three.bin"
echo "   Three bytes, a format that wants four. The unit that OVERLAPS the end"
echo "   gets 63 plus a zero byte and prints 0063: the padding is real and it is"
echo "   inside a number you might read as data. There is no 00 in the file."

echo
echo "3. UNITS ENTIRELY PAST THE END BECOME SPACES, AND THE LAST ITERATION LOSES ITS TRAILING SPACE"
show "hexdump -e '4/2 \"%04x \" \"|\n\"' one.bin | cat -vet"
show "hexdump -e '4/2 \"%04x \" \"|\n\"' eight.bin | cat -vet"
echo "   One byte, four two-byte units. Unit 1 overlaps the end and prints 0061;"
echo "   units 2 to 4 are past it and print as many spaces as they would have"
echo "   printed characters. With a full block every unit prints, and the space"
echo "   after the LAST one is dropped — which is why a full line ends '6867|'"
echo "   and the short one is exactly as wide. This is where the trailing spaces"
echo "   on every dump tool's short last line come from."

echo
echo "4. THE BLOCK IS THE LONGEST FORMAT STRING, AND A SHORTER ONE GROWS TO FIT"
show "hexdump -e '8/1 \"%02x \" \"\n\"' -e '\"%_p\"' -e '\"\n\"' eight.bin"
show "hexdump -e '8/1 \"%02x \" \"\n\"' -e '\"%_p\" \"\n\"' eight.bin"
echo "   The block is eight bytes because the first string wants eight. The second"
echo "   string asked for ONE %_p with no count, and the man page's rule is exact:"
echo "   a string whose LAST unit consumes bytes and has no iteration count has"
echo "   that count raised until the block is used up — so it printed all eight."
echo "   Move the \"\\n\" into the same string and %_p is no longer the last unit:"
echo "   the rule does not fire, one character prints, and seven bytes go unshown."
echo "   Every -e string sees the same block from its start either way."

echo
echo "5. %_u NAMES THE CONTROL CHARACTERS"
show "hexdump -e '8/1 \"%_u \" \"\n\"' ctl.bin | cat -vet"
show "hexdump -e '8/1 \"%_c \" \"\n\"' ctl.bin | cat -vet"
show "hexdump -e '8/1 \"%_p \" \"\n\"' ctl.bin | cat -vet"
echo "   Three ways to draw a byte you cannot draw. %_u prints the ASCII control"
echo "   name in lower case (ht, lf, nul, del); %_c prints the C escape where one"
echo "   exists (\\t, \\n, \\0) and three-digit octal otherwise (177 for DEL);"
echo "   %_p gives up with a dot. Two units were past the end: spaces again."

echo
echo "6. -f: THE FORMAT STRINGS IN A FILE, ONE PER LINE, # FOR A COMMENT"
cat > perusal.fmt <<'FMT'
# offsets in decimal, then the bytes, then the text — a hexdump -C in decimal
"%06.6_ad  " 8/1 "%02x " "  " 8/1 "%02x "
"  |" 16/1 "%_p" "|\n"
FMT
show "hexdump -f perusal.fmt s.txt"
echo "   -e strings and -f files are applied in the order given, and a format"
echo "   file is the one place a layout you use every day can live."

echo
echo "7. THE OFFSET IS CUMULATIVE ACROSS FILES"
show "hexdump -C three.bin eight.bin"
echo "   Two files, one dump: eight.bin's first byte is at offset 3. hexdump is"
echo "   a filter over the concatenation, which is exactly what cat a b | hexdump"
echo "   would have shown — the file boundary is not in the output anywhere."

echo
echo "8. -s TAKES 0x, AND -n COUNTS FROM THERE"
show "hexdump -C -s 0x8 -n 4 s.txt"
echo "   A leading 0x makes the offset hexadecimal, a leading 0 makes it octal,"
echo "   plain digits are decimal — the C rules. The offset column still shows"
echo "   the position in the file, not in the window."

echo
echo "9. EXIT STATUS: 0, AND >0 IF A FILE CANNOT BE READ"
hexdump -C s.txt > /dev/null; echo "   hexdump -C s.txt          -> $?"
hexdump -C no_such_file > /dev/null 2>&1 && st=0 || st=$?; echo "   hexdump -C no_such_file   -> $st  (message on stderr, not shown)"
