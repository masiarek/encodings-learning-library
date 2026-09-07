#!/usr/bin/env bash
# base64 on a real pipe, and the parts of it that are safe to write down.
#
# Everything this script RUNS is byte-identical on macOS and Ubuntu. That is a
# narrower set than it looks: the base64 command's flags, its default line
# wrapping and its tolerance of damaged input all differ between the BSD and
# GNU builds, so those are described here and measured in a dated table on the
# page rather than run.
#
# Run:  bash binary_to_text_sh.sh

set -u

WORD='café'

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

say "1. THE ROUND TRIP"
printf '   %-24s %s\n' 'the text' "$WORD"
printf '   %-24s ' 'base64';               printf '%s' "$WORD" | base64
printf '   %-24s ' 'base64 | --decode';    printf '%s' "$WORD" | base64 | base64 --decode; printf '\n'
printf '\n   --decode is the spelling to use. -d works on both builds too;\n'
printf '   -D is macOS only and GNU rejects it outright, which is the good\n'
printf '   kind of incompatibility -- the script stops instead of guessing.\n'

say "2. base64 IS THE HEX DUMP, RE-CUT"
printf '   %-24s ' 'xxd -p     (4 bits/char)'; printf '%s' "$WORD" | xxd -p
printf '   %-24s ' 'base64     (6 bits/char)'; printf '%s' "$WORD" | base64
printf '   %-24s %s\n' 'bytes in' "$(printf '%s' "$WORD" | wc -c | tr -d ' ')"
printf '   %-24s %s\n' 'hex chars out'  "$(printf '%s' "$WORD" | xxd -p | tr -d '\n' | wc -c | tr -d ' ')"
printf '   %-24s %s\n' 'base64 chars out' "$(printf '%s' "$WORD" | base64 | tr -d '\n' | wc -c | tr -d ' ')"
printf '\n   Same five bytes, two widths. Hex spends a character on every four\n'
printf '   bits and doubles the size; base64 spends one on every six and adds\n'
printf '   a third. Neither has looked at a character in the text -- xxd and\n'
printf '   base64 are both reading the same five bytes off the same pipe.\n'

say "3. ONE WORD, TWO CHARSETS, TWO BASE64 STRINGS"
printf '   %-24s ' 'as utf-8';      printf '%s' "$WORD" | base64
printf '   %-24s ' 'as iso-8859-1'; printf '%s' "$WORD" | iconv -f UTF-8 -t ISO-8859-1 | base64
printf '\n   Both are valid base64 of a word spelled the same way, and nothing\n'
printf '   in either string says which encoding produced the bytes. That is\n'
printf '   not a flaw in base64: base64 was never told. If an interface\n'
printf '   agreement says "the field is base64", it has not said enough.\n'

say "4. NEWLINES INSIDE THE PAYLOAD ARE FINE -- ON BOTH BUILDS"
printf '   %-24s ' 'Y2Fm\nw6k= --decode'; printf 'Y2Fm\nw6k=\n' | base64 --decode; printf '\n'
printf '\n   Line breaks are part of the deal: MIME wrapped base64 at 76\n'
printf '   characters and every decoder skips them. What is NOT portable is\n'
printf '   anything past that. A space in the middle of the payload is\n'
printf '   decoded straight through by the macOS build (exit 0) and rejected\n'
printf '   by GNU after partial output (exit 1); the default wrap width is\n'
printf '   none on macOS and 76 on GNU; the flag that sets it is -b on macOS\n'
printf '   and -w on GNU; and -i means "input file" on macOS and "ignore\n'
printf '   garbage" on GNU. See the table on the page.\n'

say "5. DECODE, THEN VALIDATE -- TWO STEPS, NOT ONE"
printf '   %-24s ' 'decoded bytes';   printf '%s' "$WORD" | base64 | base64 --decode | xxd -p
if printf '%s' "$WORD" | base64 | base64 --decode | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1; then
  printf '   %-24s %s\n' 'valid UTF-8?' 'yes (iconv exit 0)'
else
  printf '   %-24s %s\n' 'valid UTF-8?' 'no (iconv exit 1)'
fi
if printf 'wyj/' | base64 --decode | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1; then
  printf '   %-24s %s\n' 'and wyj/ ?' 'yes (iconv exit 0)'
else
  printf '   %-24s %s\n' 'and wyj/ ?' 'no (iconv exit 1)'
fi
printf '\n   base64 --decode succeeded on both. It always does: c3 28 ff is a\n'
printf '   perfectly good run of bytes and base64 has no opinion about text.\n'
printf '   The question "is this UTF-8?" is asked by a second tool, after,\n'
printf '   and a pipeline that never asks it is a pipeline that ships\n'
printf '   whatever it was handed.\n'
