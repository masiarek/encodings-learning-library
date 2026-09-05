#!/usr/bin/env bash
# The mark on a real pipe: both orders, the UTF-8 signature, and taking it off.
#
# Everything here is bytes going through a pipe, because the whole subject is
# what is actually in the file rather than what a program says about it.
#
# Run:  bash byte_order_and_bom_sh.sh
#
# Deliberately NOT shown: `iconv -t UTF-16` with no BE/LE. It adds a mark, and
# it picks the order itself -- big-endian on macOS, little-endian on GNU. The
# same command on two machines therefore writes two different files, so there
# is no single answer key for it. That split is the page's own point made by
# accident: even the converter will not tell you which end it chose. Look.

set -u

BOM8='\xef\xbb\xbf'

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

say "1. THE SAME TWO LETTERS, BOTH WAYS ROUND"
printf '   as UTF-16BE (most significant byte first):\n'
printf 'ID' | iconv -f UTF-8 -t UTF-16BE | xxd | sed 's/^/     /'
printf '\n   as UTF-16LE (least significant byte first):\n'
printf 'ID' | iconv -f UTF-8 -t UTF-16LE | xxd | sed 's/^/     /'
printf '\n   Two files, same text, no byte in common in the same place. A\n'
printf '   reader handed either one and told nothing has to guess -- and the\n'
printf '   guess is not detectable, because both are well-formed UTF-16.\n'

say "2. THE MARK, PUT IN FRONT BY HAND"
printf '   with a big-endian mark:\n'
{ printf '\xfe\xff'; printf 'ID' | iconv -f UTF-8 -t UTF-16BE; } | xxd | sed 's/^/     /'
printf '\n   with a little-endian mark:\n'
{ printf '\xff\xfe'; printf 'ID' | iconv -f UTF-8 -t UTF-16LE; } | xxd | sed 's/^/     /'
printf '\n   Now nobody is guessing. The first two bytes are the same code\n'
printf '   point written in the file'"'"'s own order, so a reader learns the\n'
printf '   order by reading. FE FF and FF FE are the whole protocol.\n'

say "3. UTF-8 HAS NO ORDER, AND STILL COLLECTS THREE BYTES"
printf '   plain UTF-8:\n'
printf 'id,name\n' | xxd | sed 's/^/     /'
printf '\n   the same, with the UTF-8 signature:\n'
printf "${BOM8}id,name\n" | xxd | sed 's/^/     /'
printf '\n   first three bytes: '
printf "${BOM8}id,name\n" | head -c 3 | xxd -p
printf '   EF BB BF is U+FEFF encoded as UTF-8. It resolves no byte order --\n'
printf '   UTF-8 has none -- it is a flag saying "this file is UTF-8", for a\n'
printf '   reader that would otherwise fall back to a local code page.\n'

say "4. TO ANYTHING ANCHORED AT THE START, IT IS CONTENT"
printf '   grep -c "^id" on the clean file      : '
printf 'id,name\n' | grep -c '^id'
printf '   grep -c "^id" on the signed file     : '
printf "${BOM8}id,name\n" | grep -c '^id'
printf '\n   Same visible text, and the second one matches nothing. The line\n'
printf '   does not start with i; it starts with EF. Nothing errors, nothing\n'
printf '   warns, the count is just zero -- which is the failure mode that\n'
printf '   costs an afternoon.\n'

say "5. AND TWO SIGNED FILES DO NOT CONCATENATE"
cat <(printf "${BOM8}a\n") <(printf "${BOM8}b\n") | xxd | sed 's/^/     /'
printf '\n   The second mark is now in the middle of the file, where it is not\n'
printf '   a signature at all -- just an invisible character glued to the "b".\n'
printf '   Anything that joins files (cat, a log shipper, a multipart upload)\n'
printf '   turns a signature into a data bug on every part after the first.\n'

say "6. TAKING IT OFF, PORTABLY"
printf '   sed on line 1 only  : '
printf "${BOM8}id,name\n" | sed "1s/^$(printf '\xef\xbb\xbf')//" | xxd -p
printf '   tail -c +4          : '
printf "${BOM8}id,name\n" | tail -c +4 | xxd -p
printf '   ..the same on a file that never had one:\n'
printf '   sed on line 1 only  : '
printf 'id,name\n' | sed "1s/^$(printf '\xef\xbb\xbf')//" | xxd -p
printf '   tail -c +4          : '
printf 'id,name\n' | tail -c +4 | xxd -p
printf '\n   Use the sed. Both strip a real mark, and both are identical on\n'
printf '   BSD and GNU -- but `tail -c +4` removes three bytes whether or not\n'
printf '   they were the mark, so on a clean file it eats the first three\n'
printf '   characters -- "id," is gone and the header now begins "name". The\n'
printf '   sed is conditional, which is what `utf-8-sig` is in Python.\n'
