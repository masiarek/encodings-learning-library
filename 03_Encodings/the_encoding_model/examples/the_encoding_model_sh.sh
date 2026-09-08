#!/usr/bin/env bash
# The bottom two layers, with real bytes on a real pipe.
#
# Sections 3 and 4 of the Python file are a claim about numbers. This is the
# same claim made out of files: one character, three encoding schemes, and the
# base64 of each -- which is the layer that is not part of the model at all.
#
# Every iconv target here names its byte order. The bare `UTF-16` spelling is
# left out on purpose; see the note at the end.
#
# Run:  bash the_encoding_model_sh.sh
set -euo pipefail

rule() { printf -- '------------------------------------------------------------------------\n'; }
say()  { printf '\n%s\n' "$1"; rule; }

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

# U+00E9, written as its UTF-8 bytes so this script does not depend on how
# the file it lives in was saved.
printf '\xc3\xa9' > e.utf8

say "1. ONE CHARACTER, FOUR SCHEMES"
printf '\n'
for scheme in UTF-8 UTF-16BE UTF-16LE UTF-32BE; do
    iconv -f UTF-8 -t "$scheme" e.utf8 > "e.$scheme"
    printf '   %-9s %2d bytes   %s\n' \
        "$scheme" "$(wc -c < "e.$scheme" | tr -d ' ')" \
        "$(xxd -p "e.$scheme")"
done
cat <<'TXT'

   The UTF-16 pair is the same 16-bit number, 00E9, written down twice
   in opposite orders. Nothing about the character changed between
   those two rows -- only the serialisation did, which is what makes
   them two schemes of one encoding form.
TXT

say "2. THE SAME BYTES, HANDED TO A TRANSFER ENCODING"
printf '\n'
for scheme in UTF-8 UTF-16BE UTF-16LE UTF-32BE; do
    printf '   %-9s %s\n' "$scheme" "$(base64 < "e.$scheme")"
done
cat <<'TXT'

   One character, four base64 strings. base64 is a transform of the
   bytes, so it inherits whatever the scheme decided and can say
   nothing about it: "the field is base64" names the wrapper and
   leaves the encoding unstated.
TXT

say "3. THE SPELLING THIS SCRIPT WILL NOT RUN"
cat <<'TXT'

   `iconv -t UTF-16`, with no BE or LE, is the compound scheme: it
   writes a byte order mark and then picks an order -- big-endian on
   macOS, little-endian on GNU. The same command therefore writes two
   different files on two machines, which is why every target above
   names its order. Same fact as the Python file's section 4, one
   tool along.
TXT
