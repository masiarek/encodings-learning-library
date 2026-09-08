#!/usr/bin/env bash
# Answer key: the same edit, three tools, and the one portable spelling.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
printf 'caf\303\251 na\303\257ve\n' > f

echo "1. THE EDIT THAT WORKS"
printf "   sed 's/é/e/'  -> %s\n" "$(sed 's/é/e/' < f)"
printf "   tr 'é' 'e'    -> %s\n" "$(tr 'é' 'e' < f 2>&1 | head -1)"
echo "   sed matched a two-byte sequence and replaced it with one byte. tr was"
echo "   given two source bytes and one replacement byte, so it maps BOTH c3"
echo "   and a9 to 'e' -- and applies that to ï as well."
echo
echo "2. WHY sed IS RIGHT WITHOUT KNOWING ANYTHING"
printf '   in the C locale: %s\n' "$(LC_ALL=C sed 's/é/e/' < f)"
echo "   Identical. sed did not consult the locale to get this right; the"
echo "   pattern is a byte sequence and the file contains that byte sequence."
echo "   Where the locale WOULD matter is a pattern like . or [[:alpha:]],"
echo "   which have to know how wide a character is."
printf '   LC_ALL=C sed "s/f./X/" -> %s\n' "$(LC_ALL=C sed 's/f./X/' < f | xxd -p)"
echo "   In the C locale . is ONE BYTE, so f. matched f and the first half of"
echo "   é -- and the a9 left behind is now an orphan, which is why the output"
echo "   above is hex rather than text: it is not valid UTF-8 any more. LC_ALL=C"
echo "   is the flag to reach for when you want no interpretation, and the trap"
echo "   when you wanted some."
echo
echo "3. THE -i SPLIT, WHICH IS A REAL PORTABILITY PROBLEM"
echo "   GNU sed:  sed -i    's/a/b/' f        (no argument)"
echo "   BSD sed:  sed -i '' 's/a/b/' f        (empty argument required)"
echo "   Neither accepts the other's spelling, so there is NO -i form that runs"
echo "   on both. The portable answer is not a clever quoting trick:"
echo "       sed 's/a/b/' f > tmp && mv tmp f"
echo "   which is also the only form that cannot half-write the file if the"
echo "   command fails."
cp f g
sed 's/é/e/' g > g.tmp && mv g.tmp g
printf '   after the portable form: %s\n' "$(cat g)"
echo
echo "4. AND THE ONE THING BOTH seds AGREE ON"
printf '   s/x/y/ with no match  exit=%d\n' "$(sed 's/zzz/y/' f >/dev/null; echo $?)"
echo "   Zero. sed does not report whether it substituted anything, so a script"
echo "   cannot tell 'edited' from 'found nothing to edit' by status alone."
echo "   That is what /q and grep -q are for, run first."
