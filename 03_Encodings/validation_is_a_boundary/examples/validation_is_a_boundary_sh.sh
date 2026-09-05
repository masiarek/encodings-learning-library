#!/usr/bin/env bash
# Is this file UTF-8? The question a shell can answer, the offset it can give you,
# and the place where its answer is not the same as Python's or Rust's.
#
# Run:  bash validation_is_a_boundary_sh.sh
#
# Deliberately NOT demonstrated below: `iconv -c` (drop invalid bytes) behaves
# differently on the two platforms this repo tests. On bad input macOS iconv
# stops at the first bad byte; GNU iconv skips it and keeps going, so the same
# command "repairs" a file into two different files. Plain iconv, used as a
# yes/no validator, agrees everywhere - which is what this script uses.

set -u

say() { printf '\n%s\n\n' "$1"; }

say "1. THE THREE SEQUENCES FROM THE SLIDE, AS BYTES ON A PIPE"
for seq in '\x7d' '\xc2\xa9' '\xe2\x89\xa0'; do
    printf '$ printf %s | xxd\n' "'$seq'"
    printf "$seq" | xxd
done

say "2. iconv FROM UTF-8 TO UTF-8 IS A VALIDATOR: EXIT 0 MEANS YES"
check() {
    printf "$1" | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1
    printf '   %-24s exit %d   %s\n' "$1" "$?" "$2"
}
check '\x7d'         'U+007D'
check '\xc2\xa9'     'U+00A9'
check '\xe2\x89\xa0' 'U+2260'
check '\x89'         'lone continuation byte'
check '\xe2\x89'     'truncated 3-byte sequence'
check '\xc0\xaf'     "overlong '/'"
check '\xe0\x80\xaf' "overlong '/' the 3-byte way"
check '\xed\xa0\x80' 'UTF-16 surrogate U+D800'
check '\xfe'         'a byte that can never appear in UTF-8'

say "3. AND THE PLACE WHERE iconv IS NOT THE SAME VALIDATOR"
check '\xf4\x90\x80\x80' 'U+110000 - one past the top of Unicode'
check '\xf5\x80\x80\x80' 'U+140000'
check '\xf7\xbf\xbf\xbf' 'U+1FFFFF'
cat <<'NOTE'
   Exit 0, on macOS and on Linux both: iconv accepts 4-byte sequences that encode
   a number above U+10FFFF. Python and Rust reject all three. Neither side is
   confused - iconv is checking the older, wider UTF-8 that ran to 31 bits, and
   RFC 3629 (2003) capped the encoding at U+10FFFF to match what UTF-16 can name.
   "Valid UTF-8" is not one question. Say which validator you asked.
NOTE

say "4. WHAT IT WROTE BEFORE IT STOPPED IS valid_up_to"
printf '$ printf %s | iconv -f UTF-8 -t UTF-8 | xxd\n' "'caf\\xc3\\xa9 \\xe9 oops'"
printf 'caf\xc3\xa9 \xe9 oops' | iconv -f UTF-8 -t UTF-8 2>/dev/null | xxd
printf '   The six bytes of "caf\xc3\xa9 " came through; the stream stopped at the bare \\xe9.\n'

say "5. SO THE OFFSET OF THE FIRST BAD BYTE IS ONE PIPELINE"
offset() {
    local n
    n=$(printf "$1" | iconv -f UTF-8 -t UTF-8 2>/dev/null | wc -c | tr -d ' ')
    printf '   %-28s valid up to byte %s\n' "$1" "$n"
}
offset 'caf\xc3\xa9 \xe9 oops'
offset 'all \xe2\x89\xa0 good'
offset '\xed\xa0\x80 at the front'
printf '   (wc -c on whatever iconv managed to emit. On a real file: iconv -f UTF-8 -t UTF-8 < f | wc -c)\n'

say "6. WHAT NO VALIDATOR CAN TELL YOU"
cat <<'NOTE'
   iconv answers "are these bytes UTF-8?" and nothing else. It cannot tell you what
   they ARE. Every byte sequence in existence is valid Latin-1, so a file that is
   valid UTF-8 is usually valid under three other encodings too, meaning something
   different in each. `file --mime-encoding` guesses; iconv verifies one guess at a
   time. Validity is a property of the bytes. The encoding is a fact about where
   they came from, and it is not in the file.
NOTE
