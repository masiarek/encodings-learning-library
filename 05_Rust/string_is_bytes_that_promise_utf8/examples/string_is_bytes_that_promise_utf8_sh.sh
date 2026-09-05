#!/usr/bin/env bash
# The byte count is not a Rust opinion. Nothing here knows what a String is.
set -u

echo "1. THE SAME TWO STRINGS, WEIGHED BY A PROGRAM THAT HAS NO STRING TYPE"
for s in "noodles" "ಠ_ಠ"; do
  # wc -c pads its number on BSD and not on GNU, so strip the spaces.
  printf '   %-10s %s bytes on the pipe\n' "$s" "$(printf '%s' "$s" | wc -c | tr -d ' ')"
done
echo "   Two different strings, one of them 3 characters long, both 7 bytes."
echo "   Look at the ragged column above: printf '%-10s' pads to ten BYTES, not ten"
echo "   characters, so the 3-character string is padded as though it were 7 wide."
echo "   The bug this library is about, biting this script, in its second line of output."
echo

echo "2. AND HERE THEY ARE"
echo
echo "\$ printf 'noodles' | xxd"
printf 'noodles' | xxd
echo
echo "\$ printf 'ಠ_ಠ' | xxd"
printf 'ಠ_ಠ' | xxd
echo
echo "   E0 B2 A0 is one character. So is the second E0 B2 A0. The 5F between them is '_'."
echo

echo "3. THE PROMISE, CHECKED BY A TOOL INSTEAD OF A TYPE"
echo "   iconv -f UTF-8 -t UTF-8 accepts or rejects; its exit status is the whole answer."
printf 'ಠ_ಠ' | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1 \
  && echo "   whole string     -> exit 0, valid UTF-8"
# Drop the final byte: the last character is now cut in half.
printf '\xe0\xb2\xa0\x5f\xe0\xb2' | iconv -f UTF-8 -t UTF-8 >/dev/null 2>&1 \
  || echo "   last byte removed -> nonzero exit, NOT valid UTF-8"
echo "   That is String::from_utf8 and bytes.decode(), as a process."
