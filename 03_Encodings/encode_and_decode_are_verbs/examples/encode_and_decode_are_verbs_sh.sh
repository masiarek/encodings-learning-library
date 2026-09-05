#!/usr/bin/env bash
# The two verbs on a real pipe, where there is no text type to hide behind.
#
# A shell pipe carries bytes and nothing else. `iconv` is the two verbs written
# out as flags -- `-f` is decode, `-t` is encode -- which makes it the clearest
# place to see that the table is an argument you supply and nothing checks.
#
# Run:  bash encode_and_decode_are_verbs_sh.sh
#
# Deliberately NOT shown below: encoding INTO a table that cannot hold the
# input (`-t ASCII` here). GNU iconv refuses with exit 1; macOS iconv silently
# transliterates and exits 0, so there is no single answer key for it. Every
# conversion below targets a table that CAN represent its input, which behaves
# the same on both. The Python example on this page shows the refusal instead.

set -u

CAFE='caf\xc3\xa9'   # "café" in UTF-8: 63 61 66 c3 a9

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

say "1. A PIPE CARRIES BYTES. THAT IS ALL IT CARRIES."
printf '$ printf %s | xxd\n' "'$CAFE'"
printf "$CAFE" | xxd
printf '   five bytes. Nothing on this pipe records that they are UTF-8,\n'
printf '   or text at all. The next command has to be told.\n'

say "2. iconv IS THE TWO VERBS, WRITTEN AS FLAGS"
printf '$ printf %s | iconv -f UTF-8 -t ISO-8859-1 | xxd\n' "'$CAFE'"
printf "$CAFE" | iconv -f UTF-8 -t ISO-8859-1 | xxd
printf '   -f UTF-8      decode these bytes under this table  -> café\n'
printf '   -t ISO-8859-1 encode that text under this table    -> 4 bytes\n'
printf '   Same message, one byte shorter, because Latin-1 spends one byte\n'
printf '   on é where UTF-8 spends two.\n'

say "3. NOTHING CHECKS -f AGAINST THE DATA"
printf '$ printf %s | iconv -f ISO-8859-1 -t UTF-8 | xxd\n' "'$CAFE'"
printf "$CAFE" | iconv -f ISO-8859-1 -t UTF-8 | xxd
printf '   iconv exit %d -- no complaint whatsoever.\n' "${PIPESTATUS[1]}"
printf '   The same five bytes, decoded under the WRONG table and re-encoded:\n'
printf '   seven bytes now, and c3 a9 has become c3 83 c2 a9. That is mojibake,\n'
printf '   made deliberately, with a command that reported success.\n'

say "4. AND BACK, BECAUSE LATIN-1 THREW NOTHING AWAY"
printf '$ ... | iconv -f UTF-8 -t ISO-8859-1 | xxd\n'
printf "$CAFE" | iconv -f ISO-8859-1 -t UTF-8 | iconv -f UTF-8 -t ISO-8859-1 | xxd
printf '   63 61 66 c3 a9 -- the five bytes we started with.\n'
printf '   The damage in step 3 was reversible because every byte survived it.\n'
printf '   That is not true of every mistake, and which ones reverse is the\n'
printf '   next lesson.\n'
