#!/usr/bin/env bash
# ASCII from the shell: number to character and back, without a language.
#
# Run:  bash a_character_is_a_number_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od lays its columns out differently on macOS (BSD) and Linux (GNU): BSD keeps a
# blank address column under -An, pads every line, and left-aligns the -c row
# where GNU right-aligns it. `tidy` re-prints every field four wide, so the same
# bytes give the same picture on both. One limit: a SPACE byte prints as blanks
# under -c and would vanish, so these examples feed od inputs with no spaces.
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%4s", $i; print "" }' | sed -e '/^$/d'; }

echo "1. CHARACTER -> NUMBER: printf's quote trick"
show "printf '%d\\n' \"'A\""
show "printf '%d %d %d\\n' \"'a\" \"'0\" \"' \""

echo
echo "2. NUMBER -> CHARACTER: an octal or hex escape"
show "printf '\\101\\102\\103\\n'"
show "printf '\\x61\\x62\\x63\\n'"

echo
echo "3. THE CONTROL CHARACTERS ARE BYTES TOO: od shows them by name"
show "printf 'a\\tb\\nc\\r\\n' | od -An -tx1 -c | tidy"

echo
echo "4. THE CASE BIT: tr flips ASCII letters by the same rule"
show "echo 'Hello, World' | tr 'a-z' 'A-Z'"

echo
echo "5. THE WHOLE TABLE IS ON YOUR MACHINE: man ascii (not run here)"
echo "   Try:  man ascii"
