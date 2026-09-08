#!/usr/bin/env bash
# The guard, built out of two iconv calls -- and the survey you run BEFORE
# touching a file.
#
# The mojibake page shows that "repair until iconv errors" does not work,
# because -t ISO-8859-1 succeeds on correct text too. This script is the
# other half: iconv has no round-trip guard, but you can compose one, and
# the missing piece is a second call that asks "is the result UTF-8?".
set -u

work=$(mkdir -p "${TMPDIR:-/tmp}/mrt.$$" && cd "${TMPDIR:-/tmp}/mrt.$$" && pwd)
trap 'rm -rf "$work"' EXIT
cd "$work"

# is_utf8 FILE -- the portable validity test. Same-to-same conversion, which
# for UTF-8 agrees on BSD and GNU iconv, exit status included.
is_utf8() {
    iconv -f UTF-8 -t UTF-8 "$1" > /dev/null 2>&1
}

# repair_once IN OUT -- undo one wrong Latin-1 decode. Writes OUT only if all
# three hold: the conversion succeeded, the result is UTF-8, and the result
# actually DIFFERS from the input. The third test is the one that is easy to
# leave out, and without it pure ASCII reports itself as "repaired" -- it
# survives the round trip untouched, which is a no-op and not a repair.
repair_once() {
    if ! iconv -f UTF-8 -t ISO-8859-1 "$1" > "$2.candidate" 2>/dev/null; then
        rm -f "$2.candidate"
        return 1
    fi
    if is_utf8 "$2.candidate" && ! cmp -s "$2.candidate" "$1"; then
        mv "$2.candidate" "$2"
        return 0
    fi
    rm -f "$2.candidate"
    return 1
}

echo "1. THE GUARD IS TWO CALLS, NOT ONE"
echo "------------------------------------------------------------------------"
printf 'caf\xc3\xa9\n' > good.txt
echo "   correct file:        $(xxd -p < good.txt)"
iconv -f ISO-8859-1 -t UTF-8 good.txt > broken1.txt
echo "   after 1 bad hop:     $(xxd -p < broken1.txt)"
iconv -f ISO-8859-1 -t UTF-8 broken1.txt > broken2.txt
echo "   after 2 bad hops:    $(xxd -p < broken2.txt)"
echo
echo "   Now repair, checking the result each time instead of trusting the"
echo "   exit status of the conversion:"
echo
cp broken2.txt cur.txt
for step in 1 2 3; do
    if repair_once cur.txt next.txt; then
        mv next.txt cur.txt
        printf '      repair %d: accepted   %s\n' "$step" "$(xxd -p < cur.txt)"
    else
        printf '      repair %d: REFUSED    (the guard rejected the candidate)\n' "$step"
        break
    fi
done
echo
echo "   current bytes: $(xxd -p < cur.txt)"
if cmp -s cur.txt good.txt; then
    echo "   identical to the original file: yes"
else
    echo "   identical to the original file: no"
fi
echo
echo "   Repair 3 is where a bare iconv pipeline keeps going: the conversion"
echo "   itself succeeds, because Latin-1 can hold 'cafe-acute' perfectly"
echo "   well. What stops the loop is the second call -- the four bytes"
echo "   63 61 66 e9 are not UTF-8, so the candidate is thrown away and the"
echo "   file is left where it was."
echo

echo "2. WHY THE SECOND CALL IS THE ONE THAT KNOWS"
echo "------------------------------------------------------------------------"
printf 'caf\xe9\n' > over.txt
iconv -f UTF-8 -t ISO-8859-1 good.txt > /dev/null 2>&1
echo "   converting the CORRECT file one hop too far: iconv exit=$?"
is_utf8 over.txt
echo "   asking whether that hop's output is UTF-8:    exit=$?"
echo
echo "   Two different questions. iconv answers 'could I convert this',"
echo "   which is yes. Only the validator answers 'is the result still the"
echo "   kind of thing I wanted', which is no. Neither call alone is a"
echo "   repair decision; the pair is."
echo

echo "3. SURVEY THE COLUMN BEFORE YOU CHANGE IT"
echo "------------------------------------------------------------------------"
: > survey.txt
printf 'Nowak\n'               >> survey.txt   # plain ASCII
printf 'caf\xc3\xa9\n'         >> survey.txt   # correct UTF-8
printf 'caf\xc3\x83\xc2\xa9\n' >> survey.txt   # one bad hop, repairable
printf 'caf?\n'                >> survey.txt   # written with errors=replace
printf 'caf\xef\xbf\xbd\n'     >> survey.txt   # read with errors=replace
echo "   five rows, one per damage mode:"
echo
printf '      %-4s %-26s %s\n' "row" "bytes" "verdict"
row=0
while IFS= read -r line; do
    row=$((row + 1))
    printf '%s\n' "$line" > one.txt
    hex=$(xxd -p < one.txt)
    if ! is_utf8 one.txt; then
        verdict="not UTF-8 at all -- read it as a code page"
    elif repair_once one.txt fixed.txt; then
        verdict="repairable -> $(xxd -p < fixed.txt)"
    elif LC_ALL=C grep -q '?' one.txt; then
        verdict="holds '?' -- byte discarded when WRITTEN"
    elif LC_ALL=C grep -q "$(printf '\xef\xbf\xbd')" one.txt; then
        verdict="holds U+FFFD -- byte discarded when READ"
    else
        verdict="valid UTF-8, no repair applies"
    fi
    printf '      %-4s %-26s %s\n' "$row" "$hex" "$verdict"
done < survey.txt
echo
echo "   Rows 4 and 5 are the ones to notice. Both are perfectly valid"
echo "   UTF-8, so nothing downstream will complain, and both have lost a"
echo "   byte for good -- row 4 in the sending system and row 5 in the"
echo "   reading one. That is the difference worth knowing before you go"
echo "   looking for whose fault it was."
echo
echo "   Row 3 is the only one a repair helps. Running the repair over the"
echo "   whole file would have left rows 1, 2, 4 and 5 untouched, because"
echo "   the guard refuses each of them -- which is what makes a"
echo "   column-wide repair safe to run at all."
