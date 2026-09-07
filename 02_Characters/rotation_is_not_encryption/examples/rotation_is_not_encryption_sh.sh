#!/usr/bin/env bash
# ROT13 from the shell: one tr, no key, and the file never changes size.
#
# Run:  bash rotation_is_not_encryption_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

echo "1. ROT13 IS ONE tr. THE 'KEY' IS THE SECOND ARGUMENT, AND IT IS ON THE SCREEN."
show "echo 'Hello, World!' | tr 'A-Za-z' 'N-ZA-Mn-za-m'"

echo
echo "2. THE SAME COMMAND UNDOES IT -- 13 + 13 = 26"
show "echo 'Hello, World!' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | tr 'A-Za-z' 'N-ZA-Mn-za-m'"

echo
echo "3. ROT47 IS ALSO ONE tr, OVER THE 94 PRINTABLE ASCII CHARACTERS"
show "echo 'Hello, World!' | tr '!-~' 'P-~!-O'"
show "echo 'Hello, World!' | tr '!-~' 'P-~!-O' | tr '!-~' 'P-~!-O'"

echo
echo "4. NOTHING MOVED. SAME BYTE COUNT, SAME RANGE, ONE BYTE PER CHARACTER."
show "printf 'Hello' | wc -c | tr -d ' '"
show "printf 'Hello' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | wc -c | tr -d ' '"
show "printf 'Hello' | xxd"
show "printf 'Hello' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | xxd"
echo "   Every byte is still 0x21..0x7E. That is what makes it survive a mail gateway,"
echo "   and it is the same property that makes it useless as protection."

echo
echo "5. THE ROTATION CANNOT LEAVE THE RANGE IT WAS GIVEN"
show "printf 'caf\\xc3\\xa9\\n' | tr 'A-Za-z' 'N-ZA-Mn-za-m' | xxd"
echo "   The two bytes c3 a9 are outside A-Za-z, so tr passes them through untouched."
echo "   In UTF-8 that is one character, e-acute -- and no shell rotation will ever touch it."
echo "   To rotate THAT you need code points, not bytes. See the Python and Rust examples."
