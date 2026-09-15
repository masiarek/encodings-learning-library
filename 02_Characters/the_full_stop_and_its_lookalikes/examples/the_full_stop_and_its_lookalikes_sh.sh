#!/usr/bin/env bash
# A hex dump draws '.' for bytes that are not a dot, and draws three different
# byte strings as the same '...'. Then grep, whose '.' is one byte in the C
# locale -- so a look-alike is three characters long to it.
#
# Run:  bash the_full_stop_and_its_lookalikes_sh.sh
set -eu

# The runner already sets this. It is set again here, in view, because
# section 3's answers depend on it and a reader's terminal is usually UTF-8.
export LC_ALL=C

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

# Three words, one per line: a.b with U+002E FULL STOP, then U+2024 ONE DOT
# LEADER and U+2026 HORIZONTAL ELLIPSIS where the dot was. Octal escapes,
# because they mean the same bytes to every printf there is.
words() { printf 'a.b\na\342\200\244b\na\342\200\246b\n'; }

echo "1. THE TEXT COLUMN DRAWS A DOT FOR EVERY BYTE IT HAS NO PICTURE FOR"
show "printf 'hi\\n\\t.' | xxd"
echo "   Three dots on the right and one 2e on the left. The first two are"
echo "   0a (newline) and 09 (tab): the dump's placeholder, not a full stop."

echo
echo "2. THREE DIFFERENT STRINGS, ONE PICTURE"
show "printf '...' | xxd"
show "printf '\\342\\200\\246' | xxd"
show "printf '\\342\\200\\244' | xxd"
echo "   Three full stops, one HORIZONTAL ELLIPSIS, one ONE DOT LEADER. The"
echo "   text column says '...' three times; only the first dump holds a 2e,"
echo "   and the other two hold no byte below 80 at all."

echo
echo "3. GREP IN THE C LOCALE: A DOT IS ONE BYTE, A LOOK-ALIKE IS THREE"
show "words | xxd"
show "words | grep -c 'a\\.b'"
show "words | grep -c 'a.b'"
show "words | grep -c 'a...b'"
show "words | grep 'a...b' | xxd"
echo "   An escaped dot finds the one line holding byte 2e. An unescaped dot is"
echo "   any ONE byte here, so it cannot span a three-byte look-alike -- while"
echo "   'a...b', three one-byte dots, matches both look-alikes and not a.b."
