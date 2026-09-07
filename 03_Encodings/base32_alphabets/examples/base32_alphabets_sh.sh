#!/usr/bin/env bash
# Converting between the Base32 alphabets, with a tool that is on every machine.
#
# There is no `base32` on a stock macOS -- see section 1 -- so this script does
# not call one. The RFC 4648 strings below are constants, and every conversion
# is `tr`, which is the honest shape of the thing anyway: a rename is a
# character-for-character substitution and nothing more.
#
# Everything here runs identically on macOS and Ubuntu. `tr` has a real
# BSD/GNU split over multi-byte characters, but only ASCII crosses this pipe
# and LC_ALL=C is set for every example in this repository.
#
# Run:  bash base32_alphabets_sh.sh

set -u

RFC='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
HEX='0123456789ABCDEFGHIJKLMNOPQRSTUV'
CROCKFORD='0123456789ABCDEFGHJKMNPQRSTVWXYZ'
ZBASE32='ybndrfg8ejkmcpqxot1uwisza345h769'

# 'The quick brown fox jumps over the lazy dog.' in RFC 4648 base32, unpadded.
PANGRAM='KRUGKIDROVUWG2ZAMJZG653OEBTG66BANJ2W24DTEBXXMZLSEB2GQZJANRQXU6JAMRXWOLQ'

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

say "1. THE COMMAND YOU CANNOT ASSUME IS THERE"
cat <<'EOF'
   macOS 26 ships /usr/bin/base64 -- the FreeBSD one -- and there is
   no /usr/bin/base32 beside it. On the machine this was measured the
   name `base32` resolved to Homebrew's GNU coreutils 9.11 instead.
   ubuntu:24.04 has both, out of the one coreutils package.

   So a pipeline that reaches for base32 runs on a developer's Mac and
   on CI and fails on a colleague's -- with `command not found`, which
   at least stops rather than guessing. base32hex, Crockford and
   z-base-32 have no command on either platform: GNU's `basenc` covers
   base32hex, and nothing at all covers the other two.

   That is why the rest of this script is tr.
EOF

say "2. A RENAME IS ONE tr"
printf '   %-12s %s\n' 'RFC 4648'  "$PANGRAM"
printf '   %-12s %s\n' 'base32hex' "$(printf '%s' "$PANGRAM" | tr "$RFC" "$HEX")"
printf '   %-12s %s\n' 'Crockford' "$(printf '%s' "$PANGRAM" | tr "$RFC" "$CROCKFORD")"
printf '   %-12s %s\n' 'z-base-32' "$(printf '%s' "$PANGRAM" | tr "$RFC" "$ZBASE32")"
printf '\n'
printf '   %-12s %s\n' 'and back' "$(printf '%s' "$PANGRAM" | tr "$RFC" "$CROCKFORD" | tr "$CROCKFORD" "$RFC")"
printf '\n'
printf '   Four names for one encoding. Each tr is 32 characters in and 32\n'
printf '   out, one for one, so no bit has moved and the round trip is exact.\n'
printf '   Compare that with converting base32 to base64, which cannot be a\n'
printf '   tr at all: those two cut the bits into different-sized pieces, so\n'
printf '   the only way across is to decode to bytes and encode again.\n'

say "3. THE SAME FOUR VALUES, SORTED TWICE"
# Four two-byte values, already in ascending byte order.
VALUES='0011 0033 0034 00ff'
STD='AAIQ==== AAZQ==== AA2A==== AD7Q===='

printf '   %-10s %-12s %s\n' 'bytes' 'base32' 'base32hex'
i=1
for v in $VALUES; do
    s=$(printf '%s' "$STD" | cut -d' ' -f$i)
    printf '   %-10s %-12s %s\n' "$v" "$s" "$(printf '%s' "$s" | tr "$RFC" "$HEX")"
    i=$((i + 1))
done

printf '\n   sorted as base32 text:     '
printf '%s\n' $STD | sort | tr '\n' ' ' | sed 's/ $//'
printf '\n   sorted as base32hex text:  '
printf '%s\n' $STD | tr "$RFC" "$HEX" | sort | tr '\n' ' ' | sed 's/ $//'
printf '\n\n'
printf '   Read the first list against the table: sorting the base32 text\n'
printf '   puts 0034 first and 0011 second, scrambling four values that were\n'
printf '   already in order. The base32hex list is still in byte order, and\n'
printf '   RFC 4648 section 7 says that is the whole reason base32hex exists.\n'
printf '\n'
printf "   The '=' padding sorts too, which is a second reason a base32 string\n"
printf '   makes a poor sort key: it is shorter than the alphabet question and\n'
printf '   just as easy to miss.\n'

say "4. WHAT tr CANNOT DO"
printf '   %-28s %s\n' 'a Crockford typo' 'AHM6A83HENMP6TS0'
printf '   %-28s %s\n' 'the same, misread by eye' 'AHM6A83HENMP6TSO'
printf '\n'
printf '   The last character is the letter O where the data had the digit 0.\n'
printf "   Crockford's alphabet has no O, so a decoder is entitled to repair\n"
printf '   it -- and tr can do exactly that, one substitution:\n'
printf '\n'
printf '   %-28s %s\n' "tr 'IiLlOo' '111100'" "$(printf '%s' 'AHM6A83HENMP6TSO' | tr 'IiLlOo' '111100')"
printf '\n'
printf '   That repair is only available because the alphabet left those\n'
printf '   letters out. Run the same tr over an RFC 4648 string and it\n'
printf '   destroys it: I, L and O are all live symbols there, standing for\n'
printf '   8, 11 and 14, and nothing in the string says which was meant.\n'
