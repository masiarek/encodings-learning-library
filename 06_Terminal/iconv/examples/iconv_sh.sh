#!/usr/bin/env bash
# iconv: the terminal's encode/decode pair, and the four things it will not
# tell you.
#
# Everything recorded here is byte-identical on macOS (Apple's iconv) and on
# Ubuntu (GNU libiconv). Three things are NOT, and none of them is in a key:
#   * the refusal MESSAGE  - macOS prints an unrelated errno, so only the
#                            exit status is printed below
#   * //TRANSLIT's output  - a per-implementation table; the script records
#                            only that the result is pure ASCII
#   * iconv -l             - a different shape and a different length
# All three are in dated tables on the page.
#
# Run:  bash iconv_sh.sh
set -u

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

# One byte per character, and no way to tell from the file which table it means.
hx() { od -An -tx1 | tr -d '\n' | tr -s ' ' | sed 's/^ *//; s/ *$//'; }

printf 'caf\351 \244 100\n' > latin1.txt   # café ¤ 100, in ISO-8859-1

echo "1. THE ONE JOB: BYTES IN ONE TABLE, OUT IN ANOTHER"
printf '   %-24s %s\n' "the file (ISO-8859-1)" "$(hx < latin1.txt)"
iconv -f ISO-8859-1 -t UTF-8 latin1.txt > utf8.txt
printf '   %-24s %s\n' "-t UTF-8" "$(hx < utf8.txt)"
iconv -f UTF-8 -t ISO-8859-1 utf8.txt > back.txt
printf '   %-24s %s\n' "and back again" "$(hx < back.txt)"
echo "   e9 became c3 a9 and a4 became c2 a4: same two characters, four bytes"
echo "   instead of two. The text did not change; the agreement did."
echo "   Round trip identical: $(cmp -s latin1.txt back.txt && echo yes || echo no)"

echo
echo "2. THE NAME IS NOT THE TABLE — six spellings, one conversion"
for a in ISO-8859-1 ISO8859-1 LATIN1 latin1 CP819 L1; do
  printf '   -f %-12s -> %s\n' "$a" "$(iconv -f "$a" -t UTF-8 latin1.txt 2>/dev/null | hx)"
done
echo "   Aliases, all of them, for one table. 'iconv -l' lists what your machine"
echo "   knows — and prints a different SHAPE on the two platforms, so it is on"
echo "   the page and not here."

echo
echo "3. WHAT ICONV CANNOT DO IS DETECT"
iconv -f ISO-8859-1 -t UTF-8 utf8.txt > wrong.txt 2>/dev/null; st=$?
printf '   %-24s %s\n' "UTF-8 read as Latin-1" "$(hx < wrong.txt)"
echo "   exit=$st. Every byte 00-FF is a character in Latin-1, so decoding UTF-8"
echo "   as Latin-1 cannot fail — it can only be wrong. c3 a9 came back as"
echo "   c3 83 c2 a9, which is 'Ã©'. That is mojibake, produced silently, by a"
echo "   successful command. -f is a claim YOU make; iconv never checks it."

echo
echo "4. THE REFUSAL, AND THE ONLY PART OF IT WORTH READING"
printf 'a\351b' > bad.txt
iconv -f UTF-8 -t UTF-8 bad.txt >/dev/null 2>&1; echo "   invalid input        exit=$?"
iconv -f UTF-8 -t UTF-8 utf8.txt >/dev/null 2>&1; echo "   valid input          exit=$?"
iconv -f NOSUCHTABLE -t UTF-8 utf8.txt >/dev/null 2>&1; echo "   unknown table        exit=$?"
echo "   The exit status is the same on both platforms; the MESSAGE is not, and"
echo "   on macOS it does not describe the problem at all. Test the status."

echo
echo "5. THE THREE POLICIES FOR A CHARACTER THE TARGET CANNOT HOLD"
printf 'a\342\202\254b\n' > eur.txt          # a € b — € does not exist in ASCII
printf '   %-24s %s\n' "the file (UTF-8)" "$(hx < eur.txt)"
iconv -f UTF-8 -t ASCII eur.txt > p.txt 2>/dev/null; p=$?
printf '   %-24s exit=%s  out=%s\n' "-t ASCII" "$p" "$(hx < p.txt)"
iconv -f UTF-8 -t ASCII//IGNORE eur.txt > i.txt 2>/dev/null; i=$?
printf '   %-24s exit=%s  out=%s\n' "-t ASCII//IGNORE" "$i" "$(hx < i.txt)"
iconv -f UTF-8 -t ASCII//TRANSLIT eur.txt > t.txt 2>/dev/null
pure=$(LC_ALL=C tr -d '\000-\177' < t.txt | wc -c | tr -d ' ')
printf '   %-24s out is pure ASCII: %s, and its bytes are NOT recordable\n' \
       "-t ASCII//TRANSLIT" "$([ "$pure" = 0 ] && echo yes || echo no)"
echo "   Plain stops at the character it cannot write and keeps what came before."
echo "   //IGNORE drops it — and still exits 1, on both platforms, so a script"
echo "   under 'set -e' dies on the line that did exactly what it was asked."
echo "   //TRANSLIT substitutes: 'EUR' here, but WHAT it substitutes is a table"
echo "   that ships with the implementation. See the page."

echo
echo "6. THE VALIDATOR, AND THE ONE FAMILY IT WAVES THROUGH"
echo "   'iconv -f UTF-8 -t UTF-8' is the portable yes/no test for 'are these"
echo "   bytes valid UTF-8'. Judged on exit status, it agrees on both platforms:"
v() { printf "$2" > v.bin; b=$(hx < v.bin)
      iconv -f UTF-8 -t UTF-8 v.bin >/dev/null 2>&1
      printf '   %-22s %-17s exit=%s\n' "$1" "$b" "$?"; }
v "plain ASCII"          'abc'
v "cafe + U+00E9"        'caf\303\251'
v "lone high byte"       '\351'
v "truncated 2-byte"     '\303'
v "stray continuation"   '\200'
v "surrogate U+D800"     '\355\240\200'
v "overlong slash"       '\300\257'
v "overlong NUL"         '\300\200'
v "byte fe"              '\376'
v "U+10FFFF, the last"   '\364\217\277\277'
v "U+110000, one past"   '\364\220\200\200'
v "f5: no code point"    '\365\220\200\200'
v "five-byte sequence"   '\373\277\277\277\277'
echo "   Read the last three rows. Those bytes are not valid UTF-8 by any"
echo "   edition of the standard since 2003 — and iconv accepts them, on BOTH"
echo "   platforms, exit 0. Python and Rust refuse all three. The validator is"
echo "   right about every classic malformation and wrong about the range."
