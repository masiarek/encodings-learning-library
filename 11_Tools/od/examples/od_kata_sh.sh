#!/usr/bin/env bash
# Answer key: od's interface is a C type.
# Two things this key does not record raw. -a prints different NAMES for the
# same high bytes on the two implementations. And od's column PADDING differs
# too -- BSD pads wider than GNU -- so every od run here goes through
# `tr -s ' '` and loses its trailing spaces. The values are the claim; the
# layout is exactly what the page says you cannot quote.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'caf\303\251\n' > f

echo "od WITH NO FLAGS"
od f | tr -s ' ' | sed 's/ *$//; s/^/   /'
echo "   Two things happened before a byte was printed. The offsets are OCTAL,"
echo "   and the values are 16-bit WORDS in octal -- so neither column is in a"
echo "   base you were thinking in, and the bytes are paired into integers."
echo
echo "THE FLAG THAT ASKS FOR WHAT YOU WANTED"
od -A d -t x1 f | tr -s ' ' | sed 's/ *$//; s/^/   /'
echo "   -A d  address in decimal;  -t x1  type: heXadecimal, 1 byte at a time."
echo "   That is the whole interface. -t takes a C type letter and a size, so"
echo "   x1 x2 x4 are the same reading at three widths and d1 d2 d4 are signed"
echo "   decimals of the same bytes."
echo
echo "ONE PASS, THREE READINGS -- THE THING NO OTHER DUMP DOES"
od -A d -t x1 -t d1 -t c f | tr -s ' ' | sed 's/ *$//; s/^/   /'
echo "   Each -t adds a ROW under the same offsets, so you can line up the hex,"
echo "   the signed decimal and the C escape for one byte without running the"
echo "   file through three tools and hoping they agree about where they are."
echo
echo "WHAT THIS KEY WILL NOT PRINT, AND WHY"
echo "   od -a names each byte -- nl, sp, ht for the low ones. For bytes above"
echo "   0x7f the two implementations disagree: measured 2026-09-07, BSD od"
echo "   prints c3 and a9 as themselves, while GNU od masks the high bit and"
echo "   prints C and ) -- names for the ASCII characters 0x43 and 0x29, which"
echo "   are not in the file at all."
echo "   So od -a output cannot be quoted without naming the machine it came"
echo "   from, which makes it the wrong thing to paste into a bug report and"
echo "   the reason this page exists."
echo
echo "WHEN TO REACH FOR od ANYWAY"
echo "   It is the only dump POSIX guarantees, so it is the one that will be"
echo "   there on a stripped container or an unfamiliar Unix. The two flags to"
echo "   remember are the two that make it honest:"
echo "       od -A d -t x1 file"
echo "   and if you want the text column too, add -t c."
