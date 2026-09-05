#!/usr/bin/env bash
# Control characters, as bytes on a pipe.
#
# Run:  bash control_characters_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od lays its columns out differently on macOS (BSD) and Linux (GNU): BSD keeps a
# blank address column under -An, pads every line, and left-aligns the -c row
# where GNU right-aligns it. `tidy` re-prints every field four wide, so the same
# bytes give the same picture on both. One limit: a SPACE byte prints as blanks
# under -c and would vanish, so these examples feed od inputs with no spaces.
tidy() { awk '{ for (i = 1; i <= NF; i++) printf "%4s", $i; print "" }' | sed -e '/^$/d'; }

echo "1. od -c NAMES THE COMMON ONES; xxd JUST SHOWS A DOT"
show "printf 'a\\tb\\nc\\r\\n' | od -An -tx1 -c | tidy"
show "printf 'a\\tb\\nc\\r\\n' | xxd"

echo
echo "2. THE SAME TWO LINES, THREE WAYS TO END THEM"
show "printf 'one\\ntwo\\n'     | xxd"
show "printf 'one\\r\\ntwo\\r\\n' | xxd"
show "printf 'one\\rtwo\\r'     | xxd"

echo
echo "3. wc -l COUNTS LF BYTES, NOTHING ELSE"
show "printf 'one\\ntwo\\n'     | wc -l | tr -d ' '"
show "printf 'one\\r\\ntwo\\r\\n' | wc -l | tr -d ' '"
show "printf 'one\\rtwo\\r'     | wc -l | tr -d ' '"

echo
echo "4. cat -v SHOWS THE CR AS ^M — THE THING YOU SEE IN vim"
show "printf 'one\\r\\ntwo\\r\\n' | cat -v"

echo
echo "5. STRIP THEM: tr is always installed"
show "printf 'one\\r\\ntwo\\r\\n' | tr -d '\\r' | xxd"

echo
echo "6. THE CARET ARITHMETIC, IN BASH"
show "echo \$(( 0x49 & 0x1F ))   # Ctrl-I"
show "echo \$(( 0x4D & 0x1F ))   # Ctrl-M"

echo
echo "7. NUL CANNOT LIVE IN A SHELL VARIABLE, BUT IT CAN LIVE IN A PIPE"
show "printf 'ab\\0cd' | xxd"
show "printf 'ab\\0cd' | wc -c | tr -d ' '"
