#!/usr/bin/env bash
# Octal did not lose. It moved to the fields that are three bits wide.
#
# Run:  bash why_not_octal_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }
# od spaces its columns differently on macOS (BSD) and Linux (GNU) -- wider gaps and a
# line padded out with trailing blanks on BSD -- while printing the same numbers. The
# `tidy` helper the sibling scripts use re-prints each field four wide, which suits od's
# byte forms; these rows are six digits, so squeeze runs of blanks instead. Values are
# untouched; only whitespace is.
squeeze() { awk '{ $1 = $1 }; 1'; }

echo "1. THE TOOL NAMED AFTER OCTAL STILL DEFAULTS TO IT"
echo "   'od' is octal dump, and with no flags it prints 16-bit WORDS in octal,"
echo "   in the CPU's own byte order. Both CI runners are little-endian, so:"
show "printf 'caf\\303\\251\\n' | od | squeeze"
echo "   The file is the six bytes 63 61 66 c3 a9 0a, and not one of those three"
echo "   numbers is a byte: 0o060543 is 0x6163, which is 'ca' read backwards."
echo "   That default is a fossil of a machine whose unit was the word, not the byte."

echo
echo "2. -b IS THE FLAG THAT SHOWS BYTES IN OCTAL"
show "printf 'caf\\303\\251\\n' | od -b | squeeze"
echo "   Six bytes, three digits each: 18 octal digits, room for 54 bits, holding 48."
echo "   The same six bytes in hex are twelve digits holding 48 bits -- exactly the file,"
echo "   which is what 'the base divides the word' buys you."
show "printf 'caf\\303\\251\\n' | xxd -p"

echo
echo "3. THE ESCAPE THAT SURVIVED: \\NNN IS POSIX, \\xHH IS BASH"
show "printf '\\303\\251' | xxd     # octal escape: in POSIX printf, so it works in any shell"
show "printf '\\xc3\\xa9' | xxd     # hex escape: a bash extension, absent from POSIX"
echo "   Same two bytes, the e-acute. When a script must run under /bin/sh, the octal"
echo "   escape is the portable one -- which is the last place octal is not just legacy."
