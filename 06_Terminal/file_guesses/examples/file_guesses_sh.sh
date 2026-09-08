#!/usr/bin/env bash
# What file(1) can and cannot know about an encoding.
#
# Everything here uses --mime-encoding, which was byte-identical across
# file-5.41 (macOS 26), file-5.44 (Debian 12) and file-5.45 (Ubuntu 24.04) on
# every input below. The default English wording is NOT stable across those
# versions and appears nowhere in this script; the comparison is on the page.
#
# Run:  bash file_guesses_sh.sh
set -u
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

enc() { file -b --mime-encoding "$1"; }
hx()  { od -An -tx1 | tr -d '\n' | tr -s ' ' | sed 's/^ *//; s/ *$//'; }

echo "1. FIVE ANSWERS, AND ONLY TWO OF THEM ARE EVIDENCE"
printf 'Hello, plain ASCII.\n'          > ascii.txt
printf 'caf\303\251 \342\202\254\n'     > utf8.txt
printf '\357\273\277caf\303\251\n'      > utf8_bom.txt
printf 'caf\351 \244 100\n'             > latin1.txt
printf 'a\200b\n'                       > cp1252.txt
printf '\377\376c\000a\000f\000\351\000' > utf16le_bom.txt
printf 'c\000a\000f\000\351\000'         > utf16le_nobom.txt
printf '\000\001\002\377\376\177\000'    > blob.bin
: > empty.txt
for f in ascii.txt utf8.txt utf8_bom.txt latin1.txt cp1252.txt \
         utf16le_bom.txt utf16le_nobom.txt blob.bin empty.txt; do
  printf '   %-18s %-14s %s\n' "$f" "$(enc "$f")" "$(head -c 8 "$f" | hx)"
done
echo "   us-ascii and utf-8 are inferences from the bytes. iso-8859-1 is a"
echo "   proof of a NEGATIVE — not valid UTF-8, so some 8-bit table, and file"
echo "   does not pretend to know which. unknown-8bit is a weaker negative"
echo "   still: 8-bit, and not even a plausible ISO-8859 one. binary is a"
echo "   surrender, and the two utf-16 rows are the only lines here that rest"
echo "   on something written IN the file."

echo
echo "2. WHY A PURE-ASCII FILE IS EVERY ENCODING AT ONCE"
for t in US-ASCII ISO-8859-1 ISO-8859-2 CP1252 CP850; do
  printf '   read as %-12s -> %s\n' "$t" "$(iconv -f "$t" -t UTF-8 < ascii.txt | hx)"
done
echo "   Five tables, five identical answers. Below 0x80 they agree by"
echo "   construction, so there is no experiment that could tell them apart"
echo "   on this file. 'us-ascii' is not file being cautious — it is the"
echo "   strongest true statement available: every byte is under 128."

echo
echo "3. THE WHOLE VERDICT TURNS ON ONE BYTE"
printf 'caf\303\251\n' > one.txt
printf 'caf\351\n'     > two.txt
printf 'cafe\n'        > three.txt
for f in one.txt two.txt three.txt; do
  printf '   %-14s %-20s %s\n' "$f" "$(hx < "$f")" "$(enc "$f")"
done
echo "   Same word, three spellings. c3 a9 is a legal UTF-8 pair, so file"
echo "   validates it and says utf-8. e9 alone cannot start a UTF-8 sequence,"
echo "   so file falls through to 'it has a high byte and is not UTF-8'. That"
echo "   is the entire UTF-8-versus-Latin-1 decision: a validity check with a"
echo "   fallback, not a table lookup and not statistics."

echo
echo "4. A BOM IS A FACT — WITH TWO ASTERISKS"
printf '\357\273\277\351\351\351\n' > bom_junk.txt
printf '\377\376A\000B\000' > b16.bin
printf '\377\376\000\000A\000\000\000' > b32.bin
show() { printf '   %-30s %-24s %s\n' "$1" "$(hx < "$2")" "$(enc "$2")"; }
show "UTF-8 BOM, then invalid bytes" bom_junk.txt
show "ff fe, then A B in UTF-16LE"   b16.bin
show "ff fe, then two zero bytes"    b32.bin
echo "   First asterisk: a UTF-8 BOM does not settle it. file read the body,"
echo "   found bytes that are not UTF-8, and reported iso-8859-1 anyway — the"
echo "   mark is evidence about intent, not a licence to skip the check."
echo "   Second asterisk: ff fe IS the UTF-16LE mark and ALSO the first half"
echo "   of the UTF-32LE one. Two more zero bytes and the same prefix means a"
echo "   different encoding, so 'the BOM is a fact' is a fact about four"
echo "   bytes, not two."

echo
echo "5. FILE DOES NOT READ YOUR FILE — IT READS THE FIRST 64 KIB OF IT"
for n in 65534 65535 65536; do
  { head -c "$n" /dev/zero | tr '\000' 'a'; printf '\303\251\n'; } > "pad$n.txt"
  printf '   %6s bytes of ASCII, then c3 a9 -> %s\n' "$n" "$(enc "pad$n.txt")"
done
echo "   Three files that differ only in padding, and three different answers."
echo "   At 65534 both bytes of the e-acute fall inside the window and file"
echo "   says utf-8. At 65535 the window ends BETWEEN them: file sees a c3"
echo "   with nothing after it, which is not valid UTF-8, and reports"
echo "   iso-8859-1 for a file that is perfectly good UTF-8. At 65536 the"
echo "   character is outside the window entirely and the file reads as pure"
echo "   ASCII. The verdict is about a prefix, and the file is not the prefix."
