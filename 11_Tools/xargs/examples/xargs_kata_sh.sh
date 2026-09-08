#!/usr/bin/env bash
# Answer key: four filenames, and how many of them survive a naive pipeline.
set -eu
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT; cd "$tmp"
mkdir files; cd files
: > "plain.txt"
: > "two words.txt"
: > "O'Brien.txt"
: > 'quote".txt'
cd ..

count() { find files -type f "$@" 2>/dev/null; }

echo "THE FOUR FILES"
find files -type f | sort | sed 's/^/   /'
echo
echo "1. NAIVE: find | xargs"
n=$(find files -type f | xargs -I{} echo {} 2>/dev/null | wc -l | tr -d ' ')
st=0; find files -type f | xargs echo >/dev/null 2>&1 || st=$?
printf '   lines out: %s of 4        xargs exit: %d\n' "$n" "$st"
echo "   The apostrophe opens a quote that never closes, so xargs consumes the"
echo "   rest of the input looking for the end of it and then reports an"
echo "   unterminated quote. One filename broke the whole pipeline -- not just"
echo "   its own line."
echo
echo "2. WHY: xargs SPLITS ON MORE THAN NEWLINES"
printf 'a b\tc\nd\n' | xargs -n1 echo | sed 's/^/      /'
echo "   One line in, four arguments out. xargs splits on spaces and tabs as"
echo "   well as newlines, so 'two words.txt' was already two files before the"
echo "   quote problem started."
echo
echo "3. THE FIX, AND IT IS NOT A REFINEMENT"
n=$(find files -type f -print0 | xargs -0 -I{} echo {} | wc -l | tr -d ' ')
printf '   find -print0 | xargs -0    lines out: %s of 4\n' "$n"
echo "   NUL is the one byte a filename cannot contain -- the kernel's own API"
echo "   cannot express it -- so it is the only delimiter that can never occur"
echo "   in the data. Every other separator is a guess about what people do not"
echo "   name their files."
echo
echo "4. THE OTHER CORRECT FORM, WITH NO xargs AT ALL"
n=$(find files -type f -exec echo {} \; | wc -l | tr -d ' ')
printf '   find -exec ... \;          lines out: %s of 4\n' "$n"
echo "   find hands the name to exec directly, so nothing ever parses it as"
echo "   text. Use -exec ... + when you want them batched; it is the same"
echo "   safety with one process instead of four."
echo
echo "WHAT THIS IS REALLY ABOUT"
echo "   A filename is a bag of bytes with exactly two forbidden values: 00 and"
echo "   2f. Everything else -- spaces, quotes, newlines, escapes -- is legal,"
echo "   and every tool that treats a list of filenames as TEXT has to invent a"
echo "   convention the filesystem never agreed to."
