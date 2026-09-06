#!/usr/bin/env bash
# Two of the four escapes are simple enough to build in a pipe -- so build them.
#
# Percent-encoding and a MIME encoded-word are both just the bytes, rewritten:
# one puts a % in front of each, the other base64s the lot and writes down
# which charset produced them. Doing it with xxd and base64 makes the layering
# impossible to miss, because you can see the byte stage in the middle.
#
# Run:  bash escaping_into_ascii_sh.sh
#
# Not shown: punycode. There is no tool for it on a stock macOS or Ubuntu --
# it is the one scheme of the four that is not a rewriting of bytes, so no
# byte-pushing tool can do it. See the Python run on the page.

set -u

WORD='żółw'

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

say "1. PERCENT-ENCODING IS THE HEX DUMP WITH A % IN FRONT"
printf '   %-22s %s\n' 'the text' "$WORD"
printf '   %-22s ' 'xxd -p';            printf '%s' "$WORD" | xxd -p
printf '   %-22s ' 'sed s/../%&/g';     printf '%s' "$WORD" | xxd -p | sed 's/../%&/g' | tr 'a-f' 'A-F'
printf '\n   That is the whole scheme: every byte becomes three characters,\n'
printf '   %%XX. This pipe escapes all seven, including the ASCII w -- a real\n'
printf '   encoder leaves the unreserved set (letters, digits, - . _ ~) alone,\n'
printf '   which is why Python printed %%C5%%BC%%C3%%B3%%C5%%82w with a bare w on the\n'
printf '   end. RFC 3986 asks for upper-case hex digits, which is the tr.\n'

say "2. AND BACK, WITH printf"
for enc in '%C5%BC' '%63%61%66%C3%A9'; do
  printf '   %-22s -> ' "$enc"
  printf '%b\n' "$(printf '%s' "$enc" | sed 's/%/\\x/g')"
done
printf '\n   The pipe turns every %% into \\x and lets printf write the bytes.\n'
printf '   Note what did NOT happen: nothing checked that those bytes are\n'
printf '   valid UTF-8, and nothing could have -- a URL does not say what\n'
printf '   encoding its bytes came from. The terminal is doing the decoding,\n'
printf '   and it is guessing.\n'

say "3. THE SAME WORD, TWO CHARSETS, ONE URL SYNTAX"
printf '   %-14s ' 'as utf-8';      printf '%s' "$WORD" | iconv -f UTF-8 -t UTF-8      | xxd -p | sed 's/../%&/g' | tr 'a-f' 'A-F'
printf '   %-14s ' 'as iso-8859-2'; printf '%s' "$WORD" | iconv -f UTF-8 -t ISO-8859-2 | xxd -p | sed 's/../%&/g' | tr 'a-f' 'A-F'
printf '\n   Two different URLs for one word, both well-formed, and no part of\n'
printf '   either says which table produced it. A server that guesses wrong\n'
printf '   gets mojibake out of a perfectly valid query string. This is the\n'
printf '   one real weakness of percent-encoding and it is a design choice:\n'
printf '   the syntax has nowhere to put the answer.\n'

say "4. AN ENCODED-WORD PUTS THE ANSWER IN THE HEADER"
printf '   =?utf-8?B?%s?=\n'      "$(printf '%s' "$WORD" | base64)"
printf '   =?iso-8859-2?B?%s?=\n' "$(printf '%s' "$WORD" | iconv -f UTF-8 -t ISO-8859-2 | base64)"
printf '\n   Same two byte strings as section 3, base64 instead of %%XX, and\n'
printf '   the charset written in between the question marks. That is the\n'
printf '   difference that matters: a mail client reading either line knows\n'
printf '   what to decode it with, thirty years later, with no convention to\n'
printf '   agree on and nothing to guess.\n'
printf '\n   Reading one back is the same pipe in reverse:\n'
printf '     '; printf '%s' "$WORD" | base64 | base64 --decode | xxd -p
printf '     ^ the payload decoded to the bytes we started from\n'
