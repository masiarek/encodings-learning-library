#!/usr/bin/env bash
# paste, split, csplit and tee: the tools that move text without reading it.
# Everything here runs in the C locale, which is what the library's runner pins,
# and every line of this output is byte-identical on macOS and ubuntu:24.04.
#
# `look` is missing from this file on purpose: it is not installed on a plain
# Ubuntu (it lives in bsdextrautils), so CI cannot run it. Its session is on the
# page, in a fence labelled with the two machines it was measured on.
#
# Run:  bash look_paste_tee_split_sh.sh
set -eu

show() { printf '$ %s\n' "$1"; eval "$1"; }
run()  { printf '$ %s\n' "$1"; local st=0; eval "$1" || st=$?; printf '   exit=%d\n' "$st"; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'a1\na2\n' > c1
printf 'b1\nb2\n' > c2
printf 'c1\nc2\n' > c3
printf 'caf\303\251 na\303\257ve\n' > text.txt          # café naïve — 10 characters, 13 bytes with the newline
printf 'caf\303\251\n---\nna\303\257ve\n' > doc.txt
printf 'caf\303\251\nna\303\257ve\nzzz\n' > lines.txt      # three lines, two of them multi-byte

echo "1. paste -d TAKES A LIST OF BYTES, NOT A DELIMITER"
show "paste -d 'X' c1 c2 c3"
echo "   Three columns, one delimiter, nothing surprising."
show "paste -d 'é' c1 c2 c3 | cat -v"
echo "   One character in, two delimiters out. -d takes a LIST — paste -d ',;'"
echo "   is a documented feature, alternating between them — and that list is"
echo "   read a BYTE at a time, so é became the list {c3, a9}: M-C after the"
echo "   first column, M-) after the second. Nothing warned, and both fields"
echo "   are now separated by half a character. In a UTF-8 locale the two"
echo "   pastes disagree about this; the fence on the page has that."

echo
echo "2. split -b CUTS WHEREVER THE COUNT LANDS"
show 'xxd -p text.txt'
show 'split -b 4 text.txt piece_'
show 'for f in piece_*; do printf "%s: " "$f"; xxd -p "$f"; done'
echo "   Four bytes per piece, so the two bytes of é are now in different"
echo "   FILES: c3 ends the first piece and a9 begins the second. Same for the"
echo "   ï two pieces later."
show 'for f in piece_*; do printf "%s is valid UTF-8? " "$f"; if iconv -f UTF-8 -t UTF-8 < "$f" >/dev/null 2>&1; then echo yes; else echo NO; fi; done'
echo "   Two of the four pieces are not text at all. That is not a bug in"
echo "   split: it was asked for four bytes and it gave four bytes."
run  'cat piece_* | cmp - text.txt'
echo "   And the concatenation is the original, byte for byte. That is the"
echo "   contract worth remembering: the PIECES are not text, the JOIN is. Any"
echo "   program that reads one piece on its own — a decoder, a grep, an"
echo "   uploader that validates — is looking at a broken file."

echo
echo "3. THE FLAG THAT DOES NOT CUT A CHARACTER IS -l, AND IT COUNTS LINES"
show 'split -l 1 lines.txt line_'
show 'for f in line_*; do printf "%s: " "$f"; xxd -p "$f"; done'
show 'for f in line_*; do printf "%s is valid UTF-8? " "$f"; if iconv -f UTF-8 -t UTF-8 < "$f" >/dev/null 2>&1; then echo yes; else echo NO; fi; done'
echo "   One line per file, and a line ends at an 0a, which can never be part"
echo "   of a multi-byte UTF-8 character — every continuation byte has its top"
echo "   bit set. So -l is safe by construction, and -b never is. The flag that"
echo "   wants both (a byte budget, cut at line boundaries) is GNU-only; see"
echo "   the fence."

echo
echo "4. csplit CUTS ON A PATTERN, WHICH IS sed's WORLD"
show 'cat doc.txt'
show 'csplit -s -f cs_ doc.txt "/---/"'
show 'for f in cs_*; do printf "%s: " "$f"; xxd -p "$f"; done'
echo "   The pattern matches a LINE, so the cut is at a line boundary and the"
echo "   characters survive — and the matching line starts the SECOND piece,"
echo "   which is the part people get wrong. The pattern itself is a regex over"
echo "   bytes here, with the same reach and the same limits sed has."

echo
echo "5. tee IS THE CONTROL: IT CHANGES NOTHING, AND THAT IS THE POINT"
show "printf 'caf\\303\\251\\000\\377\\n' | tee copy.bin | xxd -p"
show 'xxd -p copy.bin'
echo "   A NUL and an ff — one byte no text tool likes and one that cannot"
echo "   appear in UTF-8 at all — and both came through in both directions"
echo "   untouched. tee has no text model to get wrong, which is exactly why it"
echo "   is the tool to put in the middle of a pipeline you do not trust:"
echo "   … | tee /tmp/raw | rest-of-pipeline, then xxd /tmp/raw to see what the"
echo "   rest of the pipeline was actually handed."
