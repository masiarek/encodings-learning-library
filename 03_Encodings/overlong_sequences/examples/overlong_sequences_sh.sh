#!/usr/bin/env bash
# One character, four spellings, and what a pipeline does with each.
#
# Run:  bash overlong_sequences_sh.sh
#
# The sibling lesson (validation_is_a_boundary) shows that `iconv -f UTF-8 -t UTF-8`
# is a yes/no validator. This script asks a different question: what happens when a
# byte-level filter runs BEFORE anything has validated, which is how shell pipelines
# are actually written.

set -u

say() { printf '\n%s\n\n' "$1"; }

say "1. THE CLOSING BRACE, SPELLED FOUR WAYS"
for seq in '\x7d' '\xc1\xbd' '\xe0\x81\xbd' '\xf0\x80\x81\xbd'; do
    printf '   $ printf %s | xxd -p\n' "'$seq'"
    printf '     %s\n' "$(printf "$seq" | xxd -p)"
done
printf '   All four carry the same seven payload bits. Only the first is UTF-8.\n'

say "2. iconv TAKES ONLY THE SHORTEST ONE"
check() {
    printf "$1" | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1
    printf '   %-20s exit %d   %s\n' "$1" "$?" "$2"
}
check '\x7d'             'the brace, as UTF-8'
check '\xc1\xbd'         'overlong, 2 bytes'
check '\xe0\x81\xbd'     'overlong, 3 bytes'
check '\xf0\x80\x81\xbd' 'overlong, 4 bytes'
printf '   Same on macOS and on Linux. Unlike the U+10FFFF cap, the shortest-form rule\n'
printf '   predates RFC 3629, so every iconv built in the last twenty years enforces it.\n'

say "3. A BYTE FILTER DOES NOT SEE THE BRACE IT IS LOOKING FOR"
strip() { LC_ALL=C tr -d '}'; }
size()  { wc -c | tr -d ' '; }
for pair in 'plain:name\x7ddrop' 'overlong:name\xc1\xbddrop'; do
    label=${pair%%:*}
    data=${pair#*:}
    before=$(printf "$data" | size)
    after=$(printf "$data" | strip | size)
    printf '   %-9s %-22s %2s bytes in, %2s out  -> filter removed %s\n' \
        "$label" "$(printf "$data" | xxd -p)" "$before" "$after" \
        "$(( before - after ))"
done
printf "   \`tr -d '}'\` is a byte filter and the overlong brace contains no 0x7D byte,\n"
printf '   so it passes through untouched. Any later stage that decodes leniently gets\n'
printf '   back the character the filter was put there to remove.\n'

say "4. SO THE ORDER OF THE PIPELINE IS THE SECURITY PROPERTY"
cat <<'NOTE'
   wrong:   cat input | tr -d '}' | do_something        # filter, then hope
   right:   iconv -f UTF-8 -t UTF-8 < input | tr -d '}' | do_something

   Validate at the top of the pipe and every stage below it is looking at bytes
   that have exactly one reading. Filter first and you are guarding a spelling,
   not a character - and there are three other spellings.
NOTE
