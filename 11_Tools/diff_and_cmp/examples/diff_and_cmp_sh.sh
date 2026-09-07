#!/usr/bin/env bash
# diff and cmp on files that only LOOK the same. Everything here runs in the C
# locale, which is what the library's runner pins — and for these two tools that
# changes almost nothing, because neither of them decodes anything in any
# locale. The one place the locale is worth asking about is -i, so section 5
# asks it twice.
#
# Only stdout is recorded. That is deliberate: cmp's two diagnostics go to
# stderr and are worded differently by the two implementations, so they are
# quoted on the page in a dated fence instead of in this key.
#
# Run:  bash diff_and_cmp_sh.sh
set -eu

show() { printf '$ %s\n' "$1"; eval "$1"; }
run()  { printf '$ %s\n' "$1"; local st=0; eval "$1" || st=$?; printf '   exit=%d\n' "$st"; }

# A UTF-8 locale, whatever this machine calls it — section 5 asks whether -i
# behaves differently in one. The NAME is never printed: it differs per machine
# and the answer does not.
utf8_locale() {
  local c
  for c in C.UTF-8 en_US.UTF-8 en_US.utf8; do
    if LC_ALL="$c" locale charmap 2>/dev/null | grep -qi 'utf-\?8'; then printf '%s' "$c"; return; fi
  done
  printf 'C'
}
UTF8=$(utf8_locale)

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf 'caf\303\251\n'  > nfc.txt      # café, composed:    63 61 66 c3 a9 0a
printf 'cafe\314\201\n' > nfd.txt      # café, decomposed:  63 61 66 65 cc 81 0a
printf 'one\r\ntwo\r\n' > dos.txt
printf 'one\ntwo\n'     > unix.txt
printf 'one\ntwo\n' | iconv -f UTF-8 -t UTF-16LE > a16.txt
printf 'one\ntwq\n' | iconv -f UTF-8 -t UTF-16LE > b16.txt
printf 'CAF\303\211\n' > upper.txt     # CAFÉ
printf 'a\302\240b\n'  > nbsp.txt      # a, NO-BREAK SPACE, b
printf 'a b\n'         > space.txt
printf 'one\n'         > nl.txt
printf 'one'           > nonl.txt      # same line, no final newline

echo "1. TWO FILES THAT PRINT THE SAME AND DIFFER ON EVERY LINE"
show 'cat nfc.txt nfd.txt'
show 'xxd -p nfc.txt'
show 'xxd -p nfd.txt'
run  'diff nfc.txt nfd.txt'
echo "   Six bytes against seven. Both files hold the word café: one spells the"
echo "   é as one composed character (c3 a9), the other as an e followed by a"
echo "   combining acute (65 cc 81). diff has no opinion about that. A line is"
echo "   the bytes between the newlines, those two byte strings are not equal,"
echo "   so it reports a change — and prints both sides, which look identical,"
echo "   because your terminal draws both spellings the same way."

echo
echo "2. cmp NAMES THE BYTE, AND CALLS IT A char"
run 'cmp nfc.txt nfd.txt'
echo "   Byte 4 is c3 in one file and 65 in the other. CHARACTER 4 is é in both."
echo "   The word in that message is POSIX's and both cmps print it; it has"
echo "   meant byte since before the distinction mattered. Read it as an offset"
echo "   into the file, never as a position in the text."
show "cmp -l nfc.txt nfd.txt 2>/dev/null | sed 's/^ *//'"
echo "   -l lists every differing byte: the offset, then the two values in"
echo "   OCTAL (303 is 0xc3). The leading spaces are stripped because the two"
echo "   cmps pad that column to different widths — the page has the fence. The"
echo "   third row is the interesting one: byte 6 is the newline in one file and"
echo "   201 in the other, so the files differ in LENGTH as well as in content."
echo "   No exit status is printed under a pipe anywhere on this page: a"
echo "   pipeline's status is the LAST command's, which here would be sed's."

echo
echo "3. THE OTHER PAIR THAT LOOKS IDENTICAL: CRLF AGAINST LF"
run  'diff dos.txt unix.txt >/dev/null'
show 'diff dos.txt unix.txt | cat -vet'
echo "   Every line changed, and raw on your screen not one of them looks"
echo "   changed: the byte that differs sits at the END of the line, where"
echo "   nothing draws it. That is why the diff is piped through cat -vet here"
echo "   — ^M\$ is CR LF and \$ alone is LF, so the left side of the change has"
echo "   one byte the right side does not. (It is also the only way to put this"
echo "   output on a page: a raw CR does not survive being recorded as an"
echo "   answer key, for the same reason it confuses everything else.)"
run 'diff --strip-trailing-cr dos.txt unix.txt'
echo "   Both diffs have that flag. It redefines the same for one run, which is"
echo "   the right answer when a Windows checkout meets a Unix one — and the"
echo "   wrong answer if you are trying to find out why the checksum changed."

echo
echo "4. diff DECIDES YOUR TEXT IS BINARY AND STOPS"
run 'diff a16.txt b16.txt'
echo "   Two UTF-16 files, one letter apart. Every other byte of UTF-16LE"
echo "   ASCII is 00, and a NUL is how diff decides a file is not text — so it"
echo "   declines to show you the line at all."
show 'diff --text a16.txt b16.txt | cat -v'
echo "   --text overrides the guess, and cat -v makes the NULs visible as ^@."
echo "   The line numbering is honest and useless at the same time: diff split"
echo "   the file at the 0a bytes, so its line 2 begins with the SECOND byte of"
echo "   the previous newline. A UTF-16 line break is 0a 00, and diff can only"
echo "   see the first half of it."
run 'cmp a16.txt b16.txt'
echo "   And cmp answers normally. The tool with no text model at all is the one"
echo "   still working on a file whose text model diff could not guess."

echo
echo "5. THE TWO FLAGS THAT LOOK LIKE THE FIX, AND ARE NOT"
run 'diff -i upper.txt nfc.txt'
echo '$ LC_ALL=<a UTF-8 locale> diff -i upper.txt nfc.txt'
st=0; LC_ALL="$UTF8" diff -i upper.txt nfc.txt >/dev/null || st=$?; printf '   exit=%d\n' "$st"
echo "   -i folds ASCII case. É and é are two bytes each, it does not touch"
echo "   them, and asking in a UTF-8 locale changes nothing — same status on"
echo "   both platforms. The locale name is not printed because it differs per"
echo "   machine and the answer does not."
run  'diff -w nbsp.txt space.txt >/dev/null'
show 'diff -w nbsp.txt space.txt | cat -v'
echo "   -w ignores whitespace, and whitespace means the ASCII space and tab. A"
echo "   NO-BREAK SPACE is c2 a0, an ordinary character to diff, so the line"
echo "   that looks like it has a space in it does not have one. Read the cat -v"
echo "   rendering carefully: M-B is c2 and M- is a0 — the space you can see in"
echo "   aM-BM- b belongs to a0's own spelling, not to the file."

echo
echo "6. THE THREE ANSWERS, AND THE ONE A SCRIPT SHOULD READ"
run 'diff nfc.txt nfc.txt'
run 'diff nfc.txt nfd.txt >/dev/null'
run 'diff nfc.txt no_such_file 2>/dev/null'
echo "   0 same, 1 differ, 2 trouble — the contract both tools keep, and the"
echo "   reason if diff a b; then is a bug: a missing file takes the same branch"
echo "   as a difference unless you test for 2."
run 'cmp -s nfc.txt nfd.txt'
echo "   -s prints nothing and answers with the status, which is the portable"
echo "   spelling: the statuses are identical everywhere and the messages are"
echo "   not."

echo
echo "7. THE LAST BYTE, WHICH ONLY ONE OF THEM WILL TELL YOU ABOUT"
run 'diff nl.txt nonl.txt'
echo "   One file ends with 0a and the other stops. The two lines are otherwise"
echo "   identical, and diff has a notation for exactly this. cmp reports it as"
echo "   an early EOF, on stderr, in wording that is not the same on the two"
echo "   platforms — so a script cannot read that either. The portable question"
echo "   is the status, or tail -c 1 | xxd -p."
