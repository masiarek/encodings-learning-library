#!/usr/bin/env bash
# The same byte through the two tables, on a real pipe.
#
# Every command here agrees on BSD and GNU iconv. The one that does not --
# the same-to-same validator over cp1252's five unassigned bytes -- is on
# the page in a dated fence instead, because there is no key that matches
# both runners.
set -u

work=$(mkdir -p "${TMPDIR:-/tmp}/w1252.$$" && cd "${TMPDIR:-/tmp}/w1252.$$" && pwd)
trap 'rm -rf "$work"' EXIT
cd "$work"

echo "1. ONE BYTE, TWO TABLES"
echo "------------------------------------------------------------------------"
printf '\x80' > byte80.bin
echo "   the file is one byte: $(xxd -p byte80.bin)"
echo
echo "   read as ISO-8859-1, written out as UTF-8:"
echo "      $(iconv -f ISO-8859-1 -t UTF-8 byte80.bin | xxd -p)   (U+0080, a C1 control)"
echo "   read as CP1252, written out as UTF-8:"
echo "      $(iconv -f CP1252 -t UTF-8 byte80.bin | xxd -p)   (U+20AC, the euro sign)"
echo
echo "   Same byte on disk. The table is not in the file, so the reader"
echo "   supplies it -- and these two readers disagree about this byte."
echo

echo "2. THE EURO CANNOT BE WRITTEN AS LATIN-1 AT ALL"
echo "------------------------------------------------------------------------"
printf '\xe2\x82\xac' > euro_utf8.bin
echo "   euro as UTF-8: $(xxd -p euro_utf8.bin)"
if iconv -f UTF-8 -t CP1252 euro_utf8.bin > to1252.bin 2>/dev/null; then
    echo "   UTF-8 -> CP1252      exit=0   bytes: $(xxd -p to1252.bin)"
else
    echo "   UTF-8 -> CP1252      exit=$?   (unexpected)"
fi
iconv -f UTF-8 -t ISO-8859-1 euro_utf8.bin > to8859.bin 2>/dev/null
echo "   UTF-8 -> ISO-8859-1  exit=$?   bytes written: $(wc -c < to8859.bin | tr -d ' ')"
echo
echo "   Not a bug and not a setting: the character is absent from the table,"
echo "   so there is nothing to write. An interface contract that says"
echo "   Latin-1 has ruled out the euro sign, whatever the sender intends."
echo "   (The message text differs between BSD and GNU iconv, so only the"
echo "   exit status is shown.)"
echo

echo "3. THE FINGERPRINT: WHICH TABLE DID THE READER USE?"
echo "------------------------------------------------------------------------"
printf '\xc3\xa9' > e_acute.bin          # UTF-8 for e-acute
echo "   e-acute as UTF-8 is $(xxd -p e_acute.bin), read back as..."
for table in ISO-8859-1 CP1252; do
    printf '      %-12s -> %s\n' "$table" "$(iconv -f "$table" -t UTF-8 e_acute.bin | xxd -p)"
done
echo "      the two are identical, so this character names no table"
echo
echo "   euro as UTF-8 is $(xxd -p euro_utf8.bin), read back as..."
for table in ISO-8859-1 CP1252; do
    printf '      %-12s -> %s\n' "$table" "$(iconv -f "$table" -t UTF-8 euro_utf8.bin | xxd -p)"
done
echo "      these differ, so this character DOES name the table"
echo
echo "   The rule behind it: the two tables differ only on 0x80-0x9F. The"
echo "   euro's UTF-8 bytes include 0x82; e-acute's (c3 a9) do not."
echo

echo "4. HOW MANY BYTES OF THE DISPUTED BLOCK EACH TABLE ACCEPTS"
echo "------------------------------------------------------------------------"
echo "   Converting each of the 32 bytes 0x80-0x9F to UTF-8, one at a time,"
echo "   and counting how many the table can turn into a character:"
for table in ISO-8859-1 CP1252; do
    ok=0
    for n in $(seq 128 159); do
        printf "$(printf '\\x%02x' "$n")" > one.bin
        if iconv -f "$table" -t UTF-8 one.bin > /dev/null 2>&1; then
            ok=$((ok + 1))
        fi
    done
    printf '      %-12s accepts %2d of 32\n' "$table" "$ok"
done
echo
echo "   Latin-1 has a character for every byte; CP1252 is missing five."
echo "   Convert to UTF-8 to ask this question, never CP1252 to CP1252 --"
echo "   see the note on the page for why the same-to-same form is not"
echo "   portable."
