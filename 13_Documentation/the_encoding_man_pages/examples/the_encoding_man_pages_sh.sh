#!/usr/bin/env bash
# Sweeping a documentation tree for a term: the recipe, and the two ways it
# silently returns nothing.  The real target is /usr/share/man, which holds a
# different set of pages on every machine -- so this script builds a corpus of
# its own, three "pages" whose contents we know, and runs the same commands
# over that.  The technique is the lesson; the numbers here are only true of
# the three files below.
set -u
cd "$(mktemp -d)" || exit 1

echo "1. THE CORPUS: THREE PAGES, AND WHICH ONE SAYS WHAT"
mkdir -p man/man1 man/man5
printf 'UTF8(5)\nThe UTF-8 encoding represents UCS-4 characters as a sequence of octets.\n' > man/man5/utf8.5
printf 'ICONV(1)\niconv -- codeset conversion utility.  Converts to and from UTF-8.\n'     > man/man1/iconv.1
printf 'BANNER(6)\nbanner -- print large banner on printer.\n'                             > man/man1/banner.1
for f in man/man5/utf8.5 man/man1/iconv.1 man/man1/banner.1; do
  printf '   %-18s %s\n' "$(basename "$f")" "$(sed -n 2p "$f" | cut -c1-46)"
done
echo

echo "2. BUILD THE FILE LIST FIRST, THEN SWEEP IT"
# sort, because find's order is the directory order and that is not portable.
find man -type f | sort > list.txt
echo "\$ find man -type f | sort > list.txt; wc -l < list.txt"
echo "   $(wc -l < list.txt | tr -d ' ')"
echo
echo "\$ xargs < list.txt grep -l -i 'UTF-8'"
xargs < list.txt grep -l -i 'UTF-8' | sort | sed 's|^|   |'
echo
echo "   Two of the three.  banner names no encoding, which is the answer we"
echo "   wanted: a sweep tells you WHICH pages to open, not what they say."
echo

echo "3. THE SAME QUESTION, ONE TERM AT A TIME"
for term in 'UTF-8' 'codeset' 'locale' 'octets'; do
  n=$(xargs < list.txt grep -l -i -- "$term" 2>/dev/null | sort -u | wc -l | tr -d ' ')
  printf '   %-10s %s file(s)\n' "$term" "$n"
done
echo
echo "   That loop is the whole method.  Point list.txt at /usr/share/man and"
echo "   the same four lines inventory every man page on your machine."
echo

echo "4. THE TRAP: TWO PIPELINES THAT FIND NOTHING AND SAY SO WITH EXIT 0"
echo "\$ grep -l -i 'UTF-8' \$(cat list.txt)     # argv, not stdin"
grep -l -i 'UTF-8' $(cat list.txt) 2>/dev/null | sort | sed 's|^|   |'
echo "   Correct here -- three files fit in argv.  At 17,000 they do not, and"
echo "   the shell fails the whole command rather than the grep: no matches,"
echo "   and nothing that looks like an error.  Always build the list, then"
echo "   feed it through xargs, which splits it into as many runs as it needs."
echo
echo "\$ grep -c -i 'UTF-8' list.txt            # greps the LIST, not the pages"
printf '   %s\n' "$(grep -c -i 'UTF-8' list.txt)"
echo "   Zero.  A filename is not its contents, and a list of filenames is a"
echo "   text file like any other -- so this reads as a real answer."
