#!/usr/bin/env bash
# The same byte on a pipe, told four different stories.
#
# `iconv -f <table>` is you naming the rulebook. Nothing on the pipe knows or
# checks it, so the same byte comes out as a different character every time you
# change your mind -- which is the whole of this lesson, at the command line.
#
# Run:  bash code_pages_sh.sh
#
# Deliberately NOT shown: converting INTO a table that cannot hold the input
# (Polish into ISO-8859-1, below). GNU iconv refuses with exit 1; macOS iconv
# silently transliterates and exits 0, so there is no single answer key. The
# Python example on this page shows that refusal instead.

set -u

LODZ='\xc5\x81\xc3\xb3\x64\xc5\xba'   # "Łódź" as UTF-8

say() { printf '\n%s\n%s\n\n' "$1" "------------------------------------------------------------------------"; }

# One byte in, its UTF-8 form and the character out.
under() {
    printf '     %-12s ' "$1"
    printf "$2" | iconv -f "$1" -t UTF-8 | xxd -p | sed 's/$/  /' | tr -d '\n'
    printf "$2" | iconv -f "$1" -t UTF-8
    printf '\n'
}

say "1. ONE BYTE ABOVE 0x7F, UNDER FIVE TABLES"
printf '   the byte e9, and what each rulebook says it is:\n'
printf '     %-12s %s\n' "table" "UTF-8 out   character"
for t in ISO-8859-1 ISO-8859-2 CP437 CP850 KOI8-R; do under "$t" '\xe9'; done
printf '\n   Five tables, four answers. Nothing about the byte changed.\n'

say "2. THE SAME FIVE TABLES, BELOW 0x7F"
printf '   the byte 41:\n'
for t in ISO-8859-1 ISO-8859-2 CP437 CP850 KOI8-R; do under "$t" '\x41'; done
printf '\n   41 is A in all of them, and 41 on the way out too. Every code page\n'
printf '   keeps the 1963 agreement for the bottom half; that is what makes\n'
printf '   them code PAGES rather than unrelated tables.\n'

say "3. ONE POLISH WORD, TWO TABLES THAT CAN BOTH WRITE IT"
printf '   starting from UTF-8:\n'
printf "$LODZ" | xxd | sed 's/^/     /'
for t in ISO-8859-2 CP1250; do
    printf '   $ iconv -f UTF-8 -t %s\n' "$t"
    printf "$LODZ" | iconv -f UTF-8 -t "$t" | xxd | sed 's/^/     /'
done
printf '\n   Same word, same length, different bytes -- they agree on Ł and ó and\n'
printf '   part company on ź. Two files, four bytes each, and no way to tell\n'
printf '   them apart except by being told.\n'

say "4. SO ASK THE PIPE WHICH ONE IT HAS"
printf "$LODZ" | iconv -f UTF-8 -t ISO-8859-2 | xxd -p | sed 's/^/     bytes: /'
printf '     table: \n'
printf '\n   There is no second line. `file`, `xxd` and every other tool can\n'
printf '   show you the bytes and none of them can tell you the table, because\n'
printf '   it was never written down anywhere. Somebody has to say.\n'
