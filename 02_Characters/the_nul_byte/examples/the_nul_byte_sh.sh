#!/usr/bin/env bash
# The NUL byte on a pipe, in a variable, and as the one separator that is safe.
#
# Run:  bash the_nul_byte_sh.sh
set -eu

show() { printf '\n$ %s\n' "$1"; eval "$1"; }

echo "1. A NUL TRAVELS THROUGH A FILE AND A PIPE JUST FINE"
show "printf 'a\\0b' | xxd"
show "printf 'a\\0b' | wc -c | tr -d ' '"

echo
echo "2. BUT IT CANNOT SURVIVE A SHELL VARIABLE"
# bash strings are C strings, so the substitution keeps the bytes up to the NUL.
# bash 5 prints a warning here and bash 3.2 (macOS) does not, so stderr is closed
# to keep the two machines' output identical; the page says what the warning is.
{ v=$(printf 'a\0b'); } 2>/dev/null
printf '\n$ v=$(printf %s); printf %s "$v" | xxd\n' "'a\\0b'" '%s'
printf '%s' "$v" | xxd
echo "   Two bytes, not three. The NUL did not survive the assignment, and neither"
echo "   would it survive being passed to a command: argv is NUL-terminated strings"
echo "   all the way down to execve(2), so no program can ever receive one."

echo
echo "3. WHICH IS EXACTLY WHY THE -0 AND -z FLAGS EXIST"
echo "   Two files. One of them has a newline in its name, which is legal."
show "printf 'holiday\\nphotos.txt\\nnotes.txt\\n' | xargs -n1 echo ' item:'"
echo "   Three items, two files. Now the same two names, NUL-separated:"
show "printf 'holiday\\nphotos.txt\\0notes.txt\\0' | xargs -0 -n1 echo ' item:'"

echo
echo "4. THE FAMILY OF FLAGS THAT MEANS 'NUL-SEPARATED'"
show "printf 'pear\\0apple\\0' | sort -z | xxd"
cat <<'EOT'
   find -print0    xargs -0        sort -z         grep -z
   tar --null -T -                 rg --null-data  read -d ''
   All one idea: use the byte the data cannot hold.
EOT

echo
echo "5. ON REAL FILES, WITH A REAL find"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
printf 'x\n' > "$tmp/$(printf 'holiday\nphotos.txt')"
printf 'x\n' > "$tmp/notes.txt"
cd "$tmp"
show "find . -type f | wc -l | tr -d ' '"
echo "   Two files, and 'how many lines' answered three."
show "find . -type f -print0 | tr -dc '\\0' | wc -c | tr -d ' '"
echo "   Counting NULs instead of lines answers two, which is the number of files."
