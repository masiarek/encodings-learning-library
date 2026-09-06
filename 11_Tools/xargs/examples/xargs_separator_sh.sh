#!/usr/bin/env bash
# xargs on filenames that are not plain ASCII. Everything here is byte-identical
# on macOS and Ubuntu; the places the two xargs differ are on the page, dated,
# because no answer key could hold both.
#
# Run:  bash xargs_separator_sh.sh
set -eu

tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

mkdir files && cd files
: > 'plain.txt'
: > 'with space.txt'
: > "O'Brien.txt"
: > 'quote".txt'
: > 'back\slash.txt'
: > "$(printf 'two\nlines.txt')"
: > 'caf'$'\303\251''.txt'
cd ..

echo "1. SEVEN FILES. COUNT THEM THREE WAYS AND GET THREE ANSWERS"
echo -n '   ls files | wc -l                              : '
ls files | wc -l | tr -d ' '
echo -n '   find files -type f | wc -l                    : '
find files -type f | wc -l | tr -d ' '
echo -n '   find files -type f -print0 | tr -dc "\\0" | wc -c : '
find files -type f -print0 | tr -dc '\0' | wc -c | tr -d ' '
echo "   Eight, eight, seven. One of the names contains a newline, so any count"
echo "   of LINES is a count of the wrong thing. Only the NUL-separated form"
echo "   answers 'how many files', because NUL is the one byte a filename"
echo "   cannot contain."

echo
echo "2. THE DEFAULT SEPARATOR IS WHITESPACE, NOT NEWLINE"
echo '$ printf "with space.txt\n" | xargs -n99 echo COUNT:'
printf 'with space.txt\n' | xargs -n99 echo COUNT:
echo '$ printf "with space.txt\n" | xargs -n1 echo ARG:'
printf 'with space.txt\n' | xargs -n1 echo ARG:
echo "   One filename went in and TWO arguments came out. xargs splits on"
echo "   spaces and tabs as well as newlines, so 'with space.txt' is 'with' and"
echo "   'space.txt' — two files that do not exist."

echo
echo "3. AND THE QUOTE CHARACTERS ARE SPECIAL"
echo '$ printf "O%sBrien.txt\\n" "'"'"'" | xargs echo'
if printf "O'Brien.txt\n" | xargs echo >/dev/null 2>&1; then
  echo "   (it ran)"
else
  echo "   (refused — exit $?)"
fi
echo "   An apostrophe in a filename is enough. No spaces, no newline, nothing"
echo "   exotic — xargs processes ' and \" and backslash as quoting before it"
echo "   hands anything over, so a perfectly ordinary Irish surname stops the"
echo "   pipeline. Both xargs refuse; they word it differently, so only the"
echo "   status is shown here. GNU's message names the fix, BSD's does not."

echo
echo "4. -print0 AND -0: THE PAIR THAT TURNS ALL OF IT OFF"
echo '$ find files -type f -print0 | xargs -0 -n1 echo FILE: | wc -l'
find files -type f -print0 | xargs -0 -n1 echo FILE: | wc -l | tr -d ' '
echo "   Eight lines for seven files, and this time that is honest: echo is"
echo "   printing a name that genuinely contains a newline. With -0 there is no"
echo "   splitting on spaces, no quote processing and no escape processing —"
echo "   the only separator is the one byte that cannot appear in a name."

echo
echo "5. THE SIZE LIMIT IS COUNTED IN BYTES, SO THE ENCODING DECIDES"
echo "   THE NUMBER OF BATCHES"
mkdir -p ascii accent
for i in 01 02 03 04 05 06 07 08 09 10; do
  : > "ascii/aaaaa$i"
  : > "accent/"$'\303\251\303\251\303\251\303\251\303\251'"$i"
done
echo "   Two directories, ten files each, every name SEVEN CHARACTERS long:"
echo -n '     ascii/aaaaa01   bytes: '; printf 'aaaaa01' | wc -c | tr -d ' '
echo -n '     accent/ééééé01  bytes: '; printf '\303\251\303\251\303\251\303\251\303\251''01' | wc -c | tr -d ' '
echo -n '   ascii  at -s 200 : '
find ascii -type f -print0 | xargs -0 -s 200 echo | wc -l | tr -d ' '
echo -n '   accent at -s 200 : '
find accent -type f -print0 | xargs -0 -s 200 echo | wc -l | tr -d ' '
echo "   batch(es). Same number of files, same number of characters in every"
echo "   name, and the accented directory needs more runs — because -s is a"
echo "   BYTE budget and é costs two. How many times your command runs is a"
echo "   function of how your filenames are spelled."

echo
echo "6. WHY THE BATCH COUNT IS NOT A DETAIL"
echo "   xargs runs the command once PER BATCH. That is invisible for rm and"
echo "   chmod, and it is a bug for anything that starts fresh each time:"
echo "     find . -print0 | xargs -0 tar -cf out.tar      <- batch 2 OVERWRITES"
echo "     find . -print0 | xargs -0 sort > sorted        <- sorted per batch"
echo "   Neither reports anything. The archive is simply short, and whether it"
echo "   is short depends on whether the filenames were ASCII."
echo "   The fix is not a bigger -s. It is to hand the LIST to a command that"
echo "   reads a list, instead of expanding it onto a command line:"
echo "     find . -print0 | tar --null -cf out.tar -T -"
echo "   -T - reads names from stdin and --null says they are NUL-separated, so"
echo "   there is one tar, no batching, and no separator to get wrong. Verified"
echo "   on bsdtar 3.5.3 and GNU tar 1.35."
